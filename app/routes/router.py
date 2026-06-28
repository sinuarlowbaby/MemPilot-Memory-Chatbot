from fastapi import APIRouter,  HTTPException, BackgroundTasks
from typing import Optional
import uuid
from app.services.mem0_service import memory
from openai import AsyncOpenAI
from dotenv import load_dotenv
from langsmith import traceable
from app.schemas.chat_request import ChatRequest
from app.services.chat_service import get_chat_response, save_chat_memory
from app.services.neo4j import add_knowledge_to_graph, search_graph

load_dotenv()

openai_client= AsyncOpenAI()
router = APIRouter()

@router.get("/")
async def root():
    return {"message": "Mem0 Chatbot API is running"}

@router.get("/info")
async def info():
    return {"message": "Mem0 Chatbot API is running"}
    
@router.post("/chat")
async def chat(chat_request: ChatRequest, background_tasks: BackgroundTasks):
    session_id = chat_request.session_id or str(uuid.uuid4())
    user_query = chat_request.user_query
    model = chat_request.model
    
    ai_response, cache_hit = await get_chat_response(user_query, session_id, model=model)
    
    # Add memory task to background tasks (so it doesn't slow down response)
    if not cache_hit:
        background_tasks.add_task(save_chat_memory, user_query, ai_response, session_id, model=model)

    background_tasks.add_task(add_knowledge_to_graph, user_query, ai_response, session_id)

    return {"response": ai_response, "session_id": session_id, "model": model, "cache_hit": cache_hit}