from datetime import datetime
import os
import redis
from app.services.mem0_service import memory
from app.services.llm_call import call_llm
from langsmith import traceable
from app.services.hashing import get_cache_key_sha256
from app.services.neo4j import add_knowledge_to_graph, search_graph

redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"), decode_responses=True)

@traceable(run_type="llm", name="get_chat_response")
async def get_chat_response(user_query: str, session_id: str, model: str = "groq/llama-3.3-70b-versatile") -> tuple[str, bool, list, list]:
    # 1. Search for relevant memories
    relevent_memories = []
    try:
        raw = memory.search(query=user_query, filters={"user_id": session_id})
        # Mem0 wraps results under a 'results' key
        relevent_memories = raw.get("results", []) if isinstance(raw, dict) else raw
    except Exception as e:
        print(f"Error searching Mem0: {e}")

    # Search graph relationships scoped to this user's session
    graph_relations = []
    try:
        graph_rels_str = await search_graph(user_query, session_id=session_id)
        graph_relations = [
            line.strip()
            for line in graph_rels_str.split("\n")
            if line.strip() and "No matching relationships" not in line
        ]
    except Exception as e:
        print(f"Error searching Neo4j: {e}")

    cache_key = get_cache_key_sha256(user_query, session_id, model=model)
    try:
        cached_response = redis_client.get(cache_key)
        if cached_response:
            print("Cache Hit! Serving response from Redis.")
            return cached_response, True, relevent_memories, graph_relations
    except Exception as e:
        print(f"Error getting cached response: {e}")
    
    print("Cache Miss. Generating new response.")

    ai_response = await call_llm(user_query, relevent_memories, session_id, model)

    try:
        redis_client.setex(cache_key, 60 * 60, ai_response)
        print("Response cached in Redis for 1 hour.")
    except Exception as e:
        print(f"Error caching response: {e}")
    
    return ai_response, False, relevent_memories, graph_relations


@traceable(run_type="tool", name="save_chat_memory")
def save_chat_memory(user_query: str, ai_response: str, session_id: str, model: str = "openai/gpt-4o"):
    # 4. Save both user query and assistant response to memory
    try:
        memory.add(
            [
                {"role": "user", "content": user_query},
                {"role": "assistant", "content": ai_response}
            ],
            user_id=session_id,
            metadata= {
                "session_id": session_id,
                "model": model,
                "timestamp": datetime.now().isoformat(),
            })
    except Exception as e:
        print(f"Error saving chat memory: {e}")
