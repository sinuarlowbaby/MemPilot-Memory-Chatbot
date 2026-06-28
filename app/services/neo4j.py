from typing import Optional
from llama_index.core import PropertyGraphIndex
import os
from llama_index.graph_stores.neo4j import Neo4jPropertyGraphStore
from llama_index.llms.openai import OpenAI
import logging
from langsmith import traceable
from neo4j import GraphDatabase
from app.services.relationship_extractor import extract_relationships

logger = logging.getLogger(__name__)

# Initialize OpenAI LLM for search engine query translation
llm = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), model="gpt-4o-mini", temperature=0.2)

# Connect LlamaIndex Graph Store (for search queries)
graph_store = Neo4jPropertyGraphStore(
    url=os.getenv("NEO4J_URL"),
    username=os.getenv("NEO4J_USERNAME"),
    password=os.getenv("NEO4J_PASSWORD")
)

graph_index = PropertyGraphIndex.from_existing(
    property_graph_store=graph_store,
    llm=llm,
    show_progress=True,
)
query_engine = graph_index.as_query_engine()

# Initialize direct Neo4j Driver (for clean structured writes)
neo4j_driver = GraphDatabase.driver(
    os.getenv("NEO4J_URL"),
    auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))
)

@traceable(run_type="tool", name="add_knowledge_to_graph")
async def add_knowledge_to_graph(query: str, ai_response: str, session_id: str) -> Optional[bool]:
    text_content = f"User asked: {query.strip()}\nAssistant answered: {ai_response.strip()}"
    
    try:
        logger.info("Extracting relationships using custom extractor...")
        facts = await extract_relationships(text_content)
        
        # If the extractor decides there's no useful long-term facts, skip storing
        if not facts.get("store", False):
            logger.info("No long-term memories extracted from this interaction. Skipping graph insert.")
            return True

        logger.info("Adding structured knowledge to Neo4j graph database...")
        
        # Define clean Cypher query to write dynamic nodes and relationships
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

        # Map entities to their custom extracted types
        entity_map = {e["name"]: e["type"] for e in facts.get("entities", [])}
        
        relationships_data = []
        for rel in facts.get("relationships", []):
            relationships_data.append({
                "source": rel["source"],
                "source_type": entity_map.get(rel["source"], "Concept"),
                "relation": rel["relation"].upper().replace(" ", "_"),
                "target": rel["target"],
                "target_type": entity_map.get(rel["target"], "Concept"),
                "confidence": rel["confidence"]
            })

        if relationships_data:
            with neo4j_driver.session() as session:
                session.run(cypher_query, relationships=relationships_data, session_id=session_id)
            logger.info(f"Structured knowledge successfully added to Neo4j: {len(relationships_data)} relations.")
        else:
            logger.info("No relationships to insert.")
            
    except Exception:
        logger.exception("Error adding structured knowledge to Neo4j")
        return None
    return True

@traceable(run_type="tool", name="search_graph")
def search_graph(query: str) -> str:
    try:
        logger.info("Searching graph...")
        response = query_engine.query(query)
        logger.info("Graph search completed.")
        return response.text
    except Exception:
        logger.exception("Error searching graph")
        return None
