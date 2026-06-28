from datetime import datetime
import os
import redis
from typing import Dict, Any
from openai import AsyncOpenAI
from app.services.mem0_service import memory
from langsmith import traceable
from app.services.hashing import get_cache_key_sha256
from app.services.neo4j import add_knowledge_to_graph, search_graph

openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
redis_client = redis.from_url(os.getenv("REDIS_URL"), decode_responses=True)

@traceable(run_type="llm", name="get_chat_response")
async def get_chat_response(user_query: str, session_id: str, model: str = "gpt-4o") -> tuple[str, bool]:
    # 1. Search for relevant memories

    cache_key = get_cache_key_sha256(user_query, session_id, model=model)
    print(cache_key)
    
    try:
        cached_response = redis_client.get(cache_key)
        if cached_response:
            print("Cache Hit! Serving response from Redis.")
            return cached_response, True
    except Exception as e:
        print(f"Error getting cached response: {e}")
    
    print("Cache Miss. Generating new response.")

    relevent_memories = memory.search(query=user_query, filters={"user_id": session_id})

    
    # 2. Build the prompt
    prompt = f"""
        You are a helpful assistant. You are given a user query and a list of relevant memories.
        Use the memories to answer the user query.

        User Query: {user_query}
        Relevant Memories: {relevent_memories}

        Answer: 
        """
    
    # 3. Get response from OpenAI
    response = await openai_client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": prompt}
        ],
    )
    
    ai_response = response.choices[0].message.content

    try:
        redis_client.setex(cache_key, 60 * 60, ai_response)
        print("Response cached in Redis for 1 hour.")
    except Exception as e:
        print(f"Error caching response: {e}")
    
    return ai_response, False


@traceable(run_type="tool", name="save_chat_memory")
def save_chat_memory(user_query: str, ai_response: str, session_id: str, model: str = "gpt-4o"):
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
