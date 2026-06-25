import os
import uuid
from typing import Dict, Any
from openai import AsyncOpenAI
from app.services.mem0_service import memory
from langsmith import traceable

openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@traceable(run_type="llm", name="get_chat_response")
async def get_chat_response(user_query: str, session_id: str) -> str:
    # 1. Search for relevant memories
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
        model="gpt-4o",
        messages=[
            {"role": "user", "content": prompt}
        ],
    )
    ai_response = response.choices[0].message.content
    
    return ai_response


@traceable(run_type="mem0", name="save_chat_memory")
def save_chat_memory(user_query: str, ai_response: str, session_id: str):
    # 4. Save both user query and assistant response to memory
    memory.add(
        [
            {"role": "user", "content": user_query},
            {"role": "assistant", "content": ai_response}
        ],
        user_id=session_id
    )
