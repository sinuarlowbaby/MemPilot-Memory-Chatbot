import os
from dotenv import load_dotenv
from mem0 import Memory

# 1. Load environment variables (e.g., OPENAI_API_KEY required by Mem0)
load_dotenv()

# 2. Configure Mem0
# Utilizing a vector database like ChromaDB for scalable memory storage
mem0_config = {
    "vector_store": {
        "provider": "qdrant",
        "enabled": True,
        "config": {
            "url": os.getenv("QDRANT_URL"),
            "collection_name": "mem0_chatbot_db"
        }
    },
    "llm": {
        "model": "gpt-4o",
        "temperature":0.5,
        "stream": True,
        "api_key": os.getenv("OPENAI_API_KEY")
    },
    "embedding": {
        "model": "text-embedding-3-small",
        "provider": "openai",
        "strip_accents": True,
        "normalize_embeddings": True,
        "batch_size": 1024,
        "api_key": os.getenv("OPENAI_API_KEY")
    },
    "cache": {
        "provider": "redis",
        "enabled": True,
        "ttl_seconds": 60*60*24*7, # 7 days

        "config": {
            "url": os.getenv("REDIS_URL")
        }
    },
}

# 3. Initialize the Memory instance globally
memory = Memory.from_config(mem0_config)

# 4. (Optional) Simplify imports for the rest of your app
__all__ = ["memory"]