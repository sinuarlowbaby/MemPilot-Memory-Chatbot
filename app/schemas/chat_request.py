from pydantic import BaseModel, Field
from typing import Optional

class ChatRequest(BaseModel):
    user_query: str = Field(..., description="The query to ask the chatbot")
    session_id: Optional[str] = Field(None, description="The session ID")