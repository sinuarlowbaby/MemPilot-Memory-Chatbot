import streamlit as st
import httpx
import uuid

st.set_page_config(
    page_title="Mem0 Chatbot",
    page_icon="🧠",
    layout="wide",
)

# --- Initialize session state ---
if "session_id" not in st.session_state:
    st.session_state.session_id = f"user-{str(uuid.uuid4())[:8]}"
if "messages" not in st.session_state:
    st.session_state.messages = []
if "show_memory" not in st.session_state:
    st.session_state.show_memory = True

# --- Sidebar ---
with st.sidebar:
    st.title("⚙️ Settings")
    st.divider()

    selected_model = st.selectbox(
        "Model",
        options=[
            "groq/llama-3.3-70b-versatile",
            "groq/llama-3.1-8b-instant",
            "openai/gpt-4o-mini",
            "openai/gpt-4o",
            "openai/gpt-4.1",
        ],
        index=0,
    )

    user_session_id = st.text_input(
        "User ID (Session ID)",
        value=st.session_state.session_id,
    )
    if user_session_id != st.session_state.session_id:
        st.session_state.session_id = user_session_id
        st.session_state.messages = []
        st.rerun()

    show_memory_panel = st.toggle("Show Memory Panel", value=st.session_state.show_memory)
    st.session_state.show_memory = show_memory_panel

    st.divider()
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.caption(f"Active session: `{st.session_state.session_id}`")

# --- Page Header ---
st.title("🧠 Mem0 Chatbot")
st.caption("Powered by OpenAI · Mem0 vector memory · Neo4j knowledge graph")
st.divider()

# --- Layout ---
if st.session_state.show_memory:
    col_chat, col_memory = st.columns([3, 2], gap="large")
else:
    col_chat = st.container()
    col_memory = None

# --- Chat Column ---
with col_chat:
    st.subheader("Conversation")

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if msg["role"] == "assistant":
                if msg.get("cache_hit"):
                    st.caption("⚡ Served from cache")
                else:
                    st.caption("🤖 Fresh response")

    if prompt := st.chat_input("Type your message here..."):
        st.session_state.messages.append({"role": "user", "content": prompt})

        payload = {
            "user_query": prompt,
            "session_id": st.session_state.session_id,
            "model": selected_model,
        }

        try:
            with st.spinner("Thinking..."):
                response = httpx.post(
                    "http://localhost:8000/chat",
                    json=payload,
                    timeout=30.0,
                )

            if response.status_code == 200:
                data = response.json()
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": data.get("response", ""),
                    "cache_hit": data.get("cache_hit", False),
                    "memories": data.get("memories", []),
                    "graph_relations": data.get("graph_relations", []),
                })
                st.rerun()
            else:
                st.error(f"Backend returned status {response.status_code}.")

        except Exception as e:
            st.error("Could not reach the FastAPI backend.")
            st.info("Make sure the server is running: `python -m app.main`")
            st.exception(e)

# --- Memory Panel Column ---
if col_memory is not None:
    with col_memory:
        st.subheader("🧠 Memory Hub")

        # Get the most recent assistant message
        last_assistant = None
        for msg in reversed(st.session_state.messages):
            if msg["role"] == "assistant":
                last_assistant = msg
                break

        memories       = last_assistant.get("memories", []) if last_assistant else []
        graph_relations = last_assistant.get("graph_relations", []) if last_assistant else []

        # Count badge line above the scroll container
        mem_count   = len(memories)
        graph_count = len(graph_relations)
        st.caption(
            f"🔹 {mem_count} vector memor{'y' if mem_count == 1 else 'ies'} · "
            f"🔮 {graph_count} graph relation{'s' if graph_count != 1 else ''}"
        )

        # ── Scrollable container (native Streamlit, no CSS) ─────────────────
        with st.container(height=620):

            # ── 1. SEMANTIC VECTOR MEMORIES ──────────────────────────────────
            st.write("**🔹 Semantic Memories (Mem0 / Qdrant)**")

            if memories:
                for idx, mem in enumerate(memories):
                    mem_text   = mem.get("memory", "—")
                    mem_id     = mem.get("id", "—")
                    score      = mem.get("score")
                    user_id    = mem.get("user_id", "—")
                    created_at = mem.get("created_at", "—")
                    updated_at = mem.get("updated_at", "—")
                    categories = mem.get("categories", [])
                    metadata   = mem.get("metadata") or {}

                    label = f"Memory {idx + 1} — {mem_text[:55]}{'…' if len(mem_text) > 55 else ''}"
                    with st.expander(label, expanded=idx == 0):

                        if score is not None:
                            st.write(f"**Relevance Score:** `{score:.4f}`")
                            st.progress(float(score))

                        st.write("**Memory Text:**")
                        st.info(mem_text)

                        c1, c2 = st.columns(2)
                        c1.metric("User ID", user_id)
                        short_id = (mem_id[:8] + "…") if len(mem_id) > 8 else mem_id
                        c2.metric("Memory ID", short_id)

                        c3, c4 = st.columns(2)
                        c3.write(f"**Created:** `{created_at}`")
                        c4.write(f"**Updated:** `{updated_at}`")

                        if categories:
                            st.write("**Categories:** " + " · ".join(f"`{c}`" for c in categories))

                        if metadata:
                            st.write("**Metadata:**")
                            st.json(metadata)
            else:
                st.caption("No vector memories retrieved for the latest turn.")

            st.divider()

            # ── 2. NEO4J GRAPH RELATIONSHIPS ─────────────────────────────────
            st.write("**🔮 Graph Relationships (Neo4j)**")

            if graph_relations:
                for rel in graph_relations:
                    parts = rel.split(" ", 2)
                    if len(parts) == 3:
                        source, relation, target = parts
                        c1, c2, c3 = st.columns([2, 2, 2])
                        c1.success(source)
                        c2.warning(f"──[{relation}]──▶")
                        c3.success(target)
                    else:
                        st.success(rel)
            else:
                st.caption("No graph relationships matched the latest query.")
