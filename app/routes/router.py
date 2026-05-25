from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def root():
    return {"message": "Mem0 Chatbot API is running"}
