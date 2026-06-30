# app/tests/unit_tests/test_chat_service.py
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.chat_service import get_chat_response

@pytest.mark.asyncio
async def test_get_chat_response_cache_hit():
    """If Redis has a cached answer, return it without calling OpenAI"""

    with patch("app.services.chat_service.redis_client") as mock_redis:
        mock_redis.get.return_value = "Cached answer"

        result, is_cache = await get_chat_response("hello", "user1")

        assert result == "Cached answer"
        assert is_cache == True
        mock_redis.get.assert_called_once()
        

@pytest.mark.asyncio
async def test_get_chat_response_calls_openai_on_cache_miss():
    """If Redis has no cache, OpenAI should be called"""

    with patch("app.services.chat_service.redis_client") as mock_redis, \
        patch("app.services.chat_service.openai_client") as mock_openai, \
        patch("app.services.chat_service.memory") as mock_memory:
        
        mock_redis.get.return_value = None
        mock_memory.search.return_value = []
        mock_openai.chat.completions.create = AsyncMock(return_value=MagicMock(choices=[MagicMock(message=MagicMock(content="AI answer"))]))

        result, is_cache = await get_chat_response("hello", "user1")

        assert result == "AI answer"
        assert is_cache == False

        mock_redis.get.assert_called_once()
        mock_openai.chat.completions.create.assert_awaited_once()
        mock_memory.search.assert_called_once()