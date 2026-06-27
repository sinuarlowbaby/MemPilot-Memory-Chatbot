import hashlib

def get_cache_key_sha256(user_query: str, session_id: str) -> str:
    """
    Generate a secure, consistent cache key from the user's query and session ID.
    """
    combined = f"{session_id}:{user_query}".encode("utf-8")
    return "cache_mem0_" + hashlib.sha256(combined).hexdigest()


def get_cache_key_md5(user_query: str, session_id: str) -> str:
    """
    Generate a faster, consistent cache key from the user's query and session ID.
    """
    combined = f"{session_id}:{user_query}".encode("utf-8")
    return "cache_mem0_" + hashlib.md5(combined).hexdigest()


def get_cache_key_blake2b(user_query: str, session_id: str) -> str:
    """
    Generate a fastest, consistent cache key from the user's query and session ID.
    """
    combined = f"{session_id}:{user_query}".encode("utf-8")
    return "cache_mem0_" + hashlib.blake2b(combined).hexdigest()

