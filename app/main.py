from fastapi import FastAPI
from dotenv import load_dotenv
import os
import logging
import uuid
from contextlib import asynccontextmanager
from app.routes.router import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup phase
    print("Starting up...")
    print("URL = http://localhost:8000")
    print("Swagger UI = http://localhost:8000/docs")
    yield
    # Shutdown phase
    print("Shutting down...")
    
app = FastAPI(lifespan=lifespan, title="Mem0 Chatbot", description="Mem0 Chatbot API", version="1.0.0")

app.include_router(router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="localhost", port=8000, reload=True)