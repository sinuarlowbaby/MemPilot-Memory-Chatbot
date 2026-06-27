import hashlib

CACHE_PREFIX = "cache:chat_response"

def get_cache_key_sha256(user_query: str, session_id: str, model: str = "gpt-4o") -> str:
    """
    Generate a secure, consistent cache key from the user's query and session ID.
    """
    normalized_query = user_query.lower().strip()
    combined = f"{session_id}:{normalized_query}:{model}".encode("utf-8")
    digest = hashlib.sha256(combined).hexdigest()
    return f"{CACHE_PREFIX}:{digest}"


def get_cache_key_md5(user_query: str, session_id: str, model: str = "gpt-4o") -> str:
    """
    Generate a faster, consistent cache key from the user's query and session ID.
    """
    normalized_query = user_query.lower().strip()
    combined = f"{session_id}:{normalized_query}:{model}".encode("utf-8")
    digest = hashlib.md5(combined).hexdigest()
    return f"{CACHE_PREFIX}:{digest}"


def get_cache_key_blake2b(user_query: str, session_id: str, model: str = "gpt-4o") -> str:
    """
    Generate a fastest, consistent cache key from the user's query and session ID.
    """
    normalized_query = user_query.lower().strip()
    combined = f"{session_id}:{normalized_query}:{model}".encode("utf-8")
    digest = hashlib.blake2b(combined).hexdigest()
    return f"{CACHE_PREFIX}:{digest}"

