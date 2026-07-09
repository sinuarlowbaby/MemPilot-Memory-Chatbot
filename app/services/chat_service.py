from datetime import datetime
import os
import logging
import redis
from typing import Tuple, List, Optional
from app.services.mem0_service import memory
from app.services.llm_call import call_llm
from langsmith import traceable
from app.services.hashing import get_cache_key_sha256
from app.services.neo4j import search_graph

logger = logging.getLogger(__name__)

redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"), decode_responses=True)


async def _get_semantic_memories(query: str, session_id: str) -> List[dict]:
    """Retrieve unstructured semantic memories from Mem0."""
    try:
        raw = memory.search(query=query, filters={"user_id": session_id})
        return raw.get("results", []) if isinstance(raw, dict) else raw
    except Exception as e:
        logger.error(f"Error searching Mem0 for session {session_id}: {e}", exc_info=True)
        return []


async def _get_graph_relations(query: str, session_id: str) -> List[str]:
    """Retrieve structured entity relationships from Neo4j."""
    try:
        graph_rels_str = await search_graph(query, session_id=session_id)
        return [
            line.strip()
            for line in graph_rels_str.split("\n")
            if line.strip() and "No matching relationships" not in line
        ]
    except Exception as e:
        logger.error(f"Error searching Neo4j for session {session_id}: {e}", exc_info=True)
        return []


def _get_cached_response(cache_key: str) -> Optional[str]:
    """Retrieve a cached answer from Redis."""
    try:
        return redis_client.get(cache_key)
    except Exception as e:
        logger.error(f"Error reading from Redis cache: {e}", exc_info=True)
        return None


def _set_cached_response(cache_key: str, value: str, ttl_seconds: int = 3600) -> None:
    """Cache a generated response in Redis."""
    try:
        redis_client.setex(cache_key, ttl_seconds, value)
    except Exception as e:
        logger.error(f"Error writing to Redis cache: {e}", exc_info=True)


@traceable(run_type="llm", name="get_chat_response")
async def get_chat_response(
    user_query: str, 
    session_id: str, 
    model: str = "groq/llama-3.3-70b-versatile"
) -> Tuple[str, bool, List[dict], List[str]]:
    """
    Orchestrate the hybrid memory retrieval, cache check, LLM call, and response caching.
    """
    relevant_memories = await _get_semantic_memories(user_query, session_id)
    graph_relations = await _get_graph_relations(user_query, session_id)

    cache_key = get_cache_key_sha256(user_query, session_id, model=model)
    cached_response = _get_cached_response(cache_key)
    
    if cached_response:
        logger.info(f"Cache Hit for session {session_id}! Serving response.")
        return cached_response, True, relevant_memories, graph_relations

    logger.info(f"Cache Miss for session {session_id}. Generating response via LLM.")

    ai_response = await call_llm(
        user_query, 
        relevant_memories, 
        graph_relations, 
        session_id, 
        model
    )

    _set_cached_response(cache_key, ai_response)

    return ai_response, False, relevant_memories, graph_relations


@traceable(run_type="tool", name="save_chat_memory")
def save_chat_memory(
    user_query: str, 
    ai_response: str, 
    session_id: str, 
    model: str = "openai/gpt-4o"
) -> None:
    """Save the chat transaction into the Mem0 vector memory database."""
    try:
        memory.add(
            [
                {"role": "user", "content": user_query},
                {"role": "assistant", "content": ai_response}
            ],
            user_id=session_id,
            metadata={
                "session_id": session_id,
                "model": model,
                "timestamp": datetime.now().isoformat(),
            }
        )
        logger.info(f"Successfully added chat transaction to Mem0 memory for session {session_id}.")
    except Exception as e:
        logger.error(f"Error saving chat transaction to Mem0 for session {session_id}: {e}", exc_info=True)
