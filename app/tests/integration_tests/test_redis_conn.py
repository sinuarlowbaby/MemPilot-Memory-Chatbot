import pytest
import redis, os
from dotenv import load_dotenv

load_dotenv()

def test_redis_connection():
    """Integration test: verifies Redis is reachable"""
    client = redis.from_url(os.getenv("REDIS_URL"), decode_responses=True)
    assert client.ping() == True  # → pytest will catch this properly

def test_redis_cache_read_write():
    """Integration test: verifies Redis can cache and retrieve data"""
    client = redis.from_url(os.getenv("REDIS_URL"), decode_responses=True)
    client.setex("test_key", 60 , "test_value")
    assert client.get("test_key") == "test_value"

    client.delete("test_key")
    assert client.get("test_key") is None