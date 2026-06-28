from typing import Optional
from llama_index.core import PropertyGraphIndex
import os
from llama_index.core import Document
from llama_index.graph_stores.neo4j import Neo4jPropertyGraphStore
from llama_index.llms.openai import OpenAI
from datetime import datetime
import logging
import json
from langsmith import traceable
from llama_index.core.indices.property_graph import SimpleLLMPathExtractor
from app.prompts.memory_prompt import MEMORY_PROMPT



logger=logging.getLogger(__name__)

llm = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), model="gpt-4o-mini", temperature=0.2)

graph_store = Neo4jPropertyGraphStore(
    url=os.getenv("NEO4J_URL"),
    username=os.getenv("NEO4J_USERNAME"),
    password=os.getenv("NEO4J_PASSWORD")
)

extractor = SimpleLLMPathExtractor(
    llm=llm,
    extract_prompt=MEMORY_PROMPT,
)

graph_index= PropertyGraphIndex.from_existing(
    property_graph_store=graph_store,
    llm=llm,
    kg_extractors=[extractor],
    show_progress=True,
    # possible_entities=[
    #     "Person",
    #     "Project",
    #     "Technology",
    #     "Framework",
    #     "Database",
    #     "Company",
    #     "Skill",
    #     "Goal",
    # ],
    # possible_relations=[
    #     "USES",
    #     "WORKS_ON",
    #     "LIKES",
    #     "LEARNS",
    #     "CREATED",
    #     "DEPENDS_ON",
    #     "PREFERS",
    # ],
    # strict=True,
)

query_engine = graph_index.as_query_engine()


@traceable(run_type="tool", name="add_knowledge_to_graph")
async def add_knowledge_to_graph(query, ai_response, session_id) -> Optional[bool]:

    text_content = f"""User Query: {query}\nSession ID: {session_id}\nAssistant Response: {ai_response}"""

    doc = Document(text = text_content,
        metadata={"session_id": session_id,
            "timestamp": datetime.utcnow().isoformat(),
            "source": "chat",
        },  
    )
    try:
        logger.info("Adding knowledge to graph...")

        graph_index.insert(doc)
        logger.info("Knowledge added to graph successfully.")
    except Exception:
        logger.exception("Error adding knowledge to graph")
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
        

