# Mem0 Chatbot API

A professional, production-ready FastAPI conversational assistant that utilizes **Mem0** for persistent hybrid memory storage (semantic vector search + graph relationships) and **Redis** for response caching.

---

## Key Features

* **Hybrid Memory Storage:** Leverages Qdrant for semantic vector facts and Neo4j for knowledge graph entity relationships.
* **LLM Response Caching:** Uses Redis to cache responses, drastically decreasing latency and OpenAI API costs for repeat queries.
* **Non-Blocking Execution:** Uses FastAPI `BackgroundTasks` to write memories asynchronously, ensuring instant response delivery.
* **Observability:** Pre-configured with LangSmith decorators for complete chain execution tracing.

---

## Tech Stack

* **Framework:** FastAPI / Uvicorn
* **Memory Management:** Mem0 (OSS)
* **LLM Integration:** OpenAI (`gpt-4o` / `gpt-4o-mini`)
* **Databases (Dockerized):** Qdrant (Vector DB), Neo4j (Graph DB), Redis (Caching)
* **Admin Dashboard:** Redis Insight (GUI)

---

## Setup & Installation

### 1. Configure Environment Variables
Create a `.env` file in the root directory:

```env
OPENAI_API_KEY="your_openai_api_key"

QDRANT_URL="http://127.0.0.1:6333"
QDRANT__SERVICE__API_KEY="secure_qdrant_api_key"

REDIS_URL="redis://127.0.0.1:6379"

NEO4J_URL="bolt://localhost:7687"
NEO4J_USERNAME="neo4j"
NEO4J_PASSWORD="password123"

LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT="https://api.smith.langchain.com"
LANGSMITH_API_KEY="your_langsmith_api_key"
LANGSMITH_PROJECT="mem0 Chatbot"
```

### 2. Start Database Services
Spin up local Qdrant, Redis, Redis Insight, and Neo4j databases:

```bash
docker compose up -d
```

### 3. Run the Backend App
Ensure your virtual environment is active, then start the server:

```bash
python -m app.main
```

The API will be live at: **http://localhost:8000**
Access the interactive Swagger documentation at: **http://localhost:8000/docs**

---

## API Usage

### `POST /chat`
Submits a user query and returns the assistant's reply.

**Request Payload:**
```json
{
  "user_query": "I enjoy coding in Python.",
  "session_id": "user_session_123"
}
```

**Response:**
```json
{
  "response": "Got it! I will remember that you like Python.",
  "session_id": "user_session_123"
}
```
