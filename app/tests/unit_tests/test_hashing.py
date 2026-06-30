import pytest
from app.services.hashing import get_cache_key_sha256

def test_same_inputs_give_same_hash():
    key1 = get_cache_key_sha256("hello", "user1", model="gpt-4o")
    key2 = get_cache_key_sha256("hello", "user1", model="gpt-4o")
    assert key1 == key2  # same inputs → same hash

def test_different_inputs_give_different_hash():
    # Note: the function normalizes case (lowercases), so 'hello' and 'world' differ
    key1 = get_cache_key_sha256("hello", "user1", model="gpt-4o")
    key2 = get_cache_key_sha256("world", "user1", model="gpt-4o")
    assert key1 != key2  # different queries → different hash

def test_case_insensitive_same_hash():
    # The function normalizes case, so 'Hello' and 'hello' produce the same key
    key1 = get_cache_key_sha256("hello", "user1", model="gpt-4o")
    key2 = get_cache_key_sha256("Hello", "user1", model="gpt-4o")
    assert key1 == key2  # case is normalized → same hash

def test_hash_is_a_string():
    key = get_cache_key_sha256("test", "user1", model="gpt-4o")
    assert isinstance(key, str)
    # Key format: 'cache:chat_response:' (20 chars) + SHA256 hex (64 chars) = 84 total
    assert len(key) == 84
    assert key.startswith("cache:chat_response:")
