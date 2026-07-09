import os
import copy
import logging
from typing import Optional
from neo4j import GraphDatabase
from langfuse.openai import AsyncOpenAI
from langfuse.decorators import observe
from app.schemas.neo4j_schema import MemoryFacts
from app.prompts.memory_prompt import MEMORY_PROMPT
from app.config import settings

logger = logging.getLogger(__name__)

# Use AsyncOpenAI directly - wraps OpenAI client with Langfuse tracing
openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

# Connect directly to Neo4j using the official driver
neo4j_driver = GraphDatabase.driver(
    settings.NEO4J_URL,
    auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD)
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


@observe(name="add_knowledge_to_graph")
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


@observe(name="search_graph")
async def search_graph(query: str, session_id: str = "") -> str:
    """
    Search relationships in Neo4j scoped to a specific user session.
    When session_id is provided, only relationships written by that user
    are returned, ensuring strict per-user data isolation.
    """
    if session_id:
        # Scoped query: only return relationships belonging to this user
        cypher_query = """
        MATCH (s:Entity)-[r]->(t:Entity)
        WHERE r.session_id = $session_id
          AND (s.name CONTAINS $search_term OR t.name CONTAINS $search_term)
        RETURN s.name + ' ' + type(r) + ' ' + t.name AS relationship
        LIMIT 10
        """
        params = {"search_term": query, "session_id": session_id}
    else:
        # Fallback: no session filter (used in tests / admin contexts only)
        cypher_query = """
        MATCH (s:Entity)-[r]->(t:Entity)
        WHERE s.name CONTAINS $search_term OR t.name CONTAINS $search_term
        RETURN s.name + ' ' + type(r) + ' ' + t.name AS relationship
        LIMIT 10
        """
        params = {"search_term": query}

    try:
        logger.info(f"Querying Neo4j for session='{session_id}' query='{query}'")
        with neo4j_driver.session() as neo4j_session:
            result = neo4j_session.run(cypher_query, **params)
            records = [record["relationship"] for record in result]
            return "\n".join(records) if records else "No matching relationships found."
    except Exception:
        logger.exception("Error searching Neo4j")
        return ""


def get_all_user_graph(session_id: str) -> list[str]:
    """
    Return ALL graph relationships stored for a specific user session.
    No text filter — used to display the full memory graph in the UI.
    """
    cypher_query = """
    MATCH (s:Entity)-[r]->(t:Entity)
    WHERE r.session_id = $session_id
    RETURN s.name + ' ' + type(r) + ' ' + t.name AS relationship
    ORDER BY r.confidence DESC
    """
    try:
        with neo4j_driver.session() as neo4j_session:
            result = neo4j_session.run(cypher_query, session_id=session_id)
            return [record["relationship"] for record in result]
    except Exception:
        logger.exception("Error fetching full user graph")
        return []
