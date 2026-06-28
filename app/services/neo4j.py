import os
import copy
import logging
from typing import Optional
from neo4j import GraphDatabase
from openai import AsyncOpenAI
from langsmith import traceable
from app.schemas.neo4j_schema import MemoryFacts
from app.prompts.memory_prompt import MEMORY_PROMPT

logger = logging.getLogger(__name__)

# Use AsyncOpenAI directly - avoids litellm schema transformation issues
openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Connect directly to Neo4j using the official driver
neo4j_driver = GraphDatabase.driver(
    os.getenv("NEO4J_URL"),
    auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))
)


def make_strict_schema(schema: dict) -> dict:
    """
    Recursively ensures all object types have:
    - "additionalProperties": false
    - all properties listed as "required"
    Required by OpenAI strict structured output mode.
    """
    schema = copy.deepcopy(schema)

    def _fix(obj):
        if not isinstance(obj, dict):
            return
        if obj.get("type") == "object" and "properties" in obj:
            obj["additionalProperties"] = False
            obj["required"] = list(obj["properties"].keys())
        for value in obj.values():
            if isinstance(value, dict):
                _fix(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        _fix(item)

    _fix(schema)
    return schema


async def extract_structured_knowledge(text_content: str) -> MemoryFacts:
    """
    Uses OpenAI's structured outputs (beta.parse) with MEMORY_PROMPT to parse
    conversation text directly into the MemoryFacts pydantic model.
    """
    response = await openai_client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": MEMORY_PROMPT},
            {"role": "user", "content": "Extract relationships from the following text:\n" + text_content}
        ],
        response_format=MemoryFacts,
        temperature=0.1
    )
    return response.choices[0].message.parsed


@traceable(run_type="tool", name="add_knowledge_to_graph")
async def add_knowledge_to_graph(query: str, ai_response: str, session_id: str) -> Optional[bool]:
    text_content = f"User asked: {query.strip()}\nAssistant answered: {ai_response.strip()}"

    try:
        logger.info("Extracting structured relationships...")
        facts = await extract_structured_knowledge(text_content)

        if not facts.store:
            logger.info("No long-term memories extracted. Skipping graph insert.")
            return True

        logger.info("Writing entities and relationships directly to Neo4j...")

        cypher_query = """
        UNWIND $relationships AS rel
        MERGE (source:Entity {name: rel.source})
        ON CREATE SET source.type = rel.source_type

        MERGE (target:Entity {name: rel.target})
        ON CREATE SET target.type = rel.target_type

        WITH source, target, rel
        CALL apoc.create.relationship(source, rel.relation, {confidence: rel.confidence, session_id: $session_id}, target)
        YIELD rel as created_rel
        RETURN count(*)
        """

        entity_map = {e.name: e.type for e in facts.entities}

        relationships_data = [
            {
                "source": rel.source,
                "source_type": entity_map.get(rel.source, "Concept"),
                "relation": rel.relation.upper().replace(" ", "_"),
                "target": rel.target,
                "target_type": entity_map.get(rel.target, "Concept"),
                "confidence": rel.confidence
            }
            for rel in facts.relationships
        ]

        if relationships_data:
            with neo4j_driver.session() as session:
                session.run(cypher_query, relationships=relationships_data, session_id=session_id)
            logger.info(f"Successfully added {len(relationships_data)} relationships to Neo4j.")
        else:
            logger.info("No relationships found to insert.")

    except Exception:
        logger.exception("Error adding structured knowledge to Neo4j")
        return None
    return True


@traceable(run_type="tool", name="search_graph")
async def search_graph(query: str) -> str:
    """
    Search relationships in Neo4j directly matching the query entity name.
    """
    cypher_query = """
    MATCH (s:Entity)-[r]->(t:Entity)
    WHERE s.name CONTAINS $query OR t.name CONTAINS $query
    RETURN s.name + ' ' + type(r) + ' ' + t.name AS relationship
    LIMIT 10
    """
    try:
        logger.info("Querying Neo4j database...")
        with neo4j_driver.session() as session:
            result = session.run(cypher_query, query=query)
            records = [record["relationship"] for record in result]
            return "\n".join(records) if records else "No matching relationships found."
    except Exception:
        logger.exception("Error searching Neo4j")
        return ""
