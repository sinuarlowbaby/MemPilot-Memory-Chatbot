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
            "collection_name": "mem0_chatbot_db",
            "api_key": os.getenv("QDRANT__SERVICE__API_KEY")
        }
    },
    "graph_store":{
        "provider": "neo4j",
        "enabled": True,
        "config": {
            "url": os.getenv("NEO4J_URL"),
            "username": os.getenv("NEO4J_USERNAME"),
            "password": os.getenv("NEO4J_PASSWORD")
        }
    },
    "llm": {
        "provider": "openai",
        "config": {
            "model": "gpt-4o-mini",
            "temperature": 0.2,
            "api_key": os.getenv("OPENAI_API_KEY")
        }
    },
    "embedder": {
        "provider": "openai",
        "config": {
            "model": "text-embedding-3-small",
            "api_key": os.getenv("OPENAI_API_KEY")
        }
    },
}

# 3. Initialize the Memory instance globally
memory = Memory.from_config(mem0_config)

# 4. (Optional) Simplify imports for the rest of your app
__all__ = ["memory"]