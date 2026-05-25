from fastapi import APIRouter,  HTTPException
from typing import Optional
import uuid
from services.mem0_service import memory
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

openai_client=OpenAI()
router = APIRouter()

@router.get("/")
async def root():
    return {"message": "Mem0 Chatbot API is running"}

@router.get("/info")
async def info():
    return {"message": "Mem0 Chatbot API is running"}
    
@router.get("/chat")
async def chat(query: str, session_id: Optional[str] = None):
    if session_id is None:
        session_id = str(uuid.uuid4())

    response = await openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": query}
        ],
        stream=True
    )
    full_response = ""
    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            full_response += chunk.choices[0].delta.content
            await memory.save_user_message(full_response, user_id=session_id)
            
    await memory.save_agent_response(full_response, user_id=session_id)
    return {"response": full_response, "session_id": session_id}