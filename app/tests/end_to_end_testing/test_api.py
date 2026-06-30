from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app

client = TestClient(app)

def test_chat_endpoint_returns_200():
    with patch("app.services.chat_service.redis_client") as mock_redis, \
         patch("app.services.chat_service.memory") as mock_memory, \
         patch("app.services.chat_service.openai_client") as mock_openai:

        mock_redis.get.return_value = "Cached!"
        response = client.post("/chat", json={
            "user_query": "hello",
            "session_id": "test_user",
            "model": "gpt-4o"
        })
        assert response.status_code == 200
        assert isinstance(response.json(), str)

def test_chat_endpoint_missing_field_returns_422():
    response = client.post("/chat", json={"session_id": "test"})  # missing user_query
    assert response.status_code == 422
