import streamlit as st
import streamlit.components.v1 as components
import httpx
import uuid
import json

def render_vis_network(graph_relations: list[dict]):
    # Extract unique nodes
    nodes_map = {}
    edges_list = []
    
    # Predefined colors for different entity types (modern premium palette)
    type_colors = {
        "person": {"background": "#DBF2FE", "border": "#0284C7", "text": "#0369A1"},
        "technology": {"background": "#FEF3C7", "border": "#D97706", "text": "#B45309"},
        "project": {"background": "#DCFCE7", "border": "#16A34A", "text": "#15803D"},
        "company": {"background": "#F3E8FF", "border": "#9333EA", "text": "#7E22CE"},
        "goal": {"background": "#FCE7F3", "border": "#DB2777", "text": "#BE185D"},
        "skill": {"background": "#E0F2FE", "border": "#0284C7", "text": "#0369A1"},
        "language": {"background": "#ECFDF5", "border": "#059669", "text": "#047857"},
        "database": {"background": "#FEF2F2", "border": "#DC2626", "text": "#B91C1C"},
        "framework": {"background": "#F0FDFA", "border": "#0D9488", "text": "#0F766E"}
    }
    default_color = {"background": "#F3F4F6", "border": "#4B5563", "text": "#374151"}
    
    for rel in graph_relations:
        if isinstance(rel, dict):
            src = rel.get("source", "")
            src_type = rel.get("source_type", "Concept")
            tgt = rel.get("target", "")
            tgt_type = rel.get("target_type", "Concept")
            relation = rel.get("relation", "")
        elif isinstance(rel, str):
            parts = rel.split(" ", 2)
            if len(parts) == 3:
                src, relation, tgt = parts
                src_type = "Concept"
                tgt_type = "Concept"
            else:
                continue
        else:
            continue
        
        # Add source node
        if src and src not in nodes_map:
            color_theme = type_colors.get(src_type.lower(), default_color)
            nodes_map[src] = {
                "id": src,
                "label": src,
                "title": f"Type: {src_type}",
                "color": color_theme,
                "font": {"color": color_theme["text"]}
            }
            
        # Add target node
        if tgt and tgt not in nodes_map:
            color_theme = type_colors.get(tgt_type.lower(), default_color)
            nodes_map[tgt] = {
                "id": tgt,
                "label": tgt,
                "title": f"Type: {tgt_type}",
                "color": color_theme,
                "font": {"color": color_theme["text"]}
            }
            
        # Add edge
        if src and tgt:
            edges_list.append({
                "from": src,
                "to": tgt,
                "label": relation,
                "font": {"color": "#6B7280", "size": 10},
                "color": {"color": "#9CA3AF", "highlight": "#6366F1"}
            })
            
    nodes_json = json.dumps(list(nodes_map.values()))
    edges_json = json.dumps(edges_list)
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
        <style type="text/css">
            #network {{
                width: 100%;
                height: 450px;
                border: 1px solid rgba(0,0,0,0.1);
                border-radius: 8px;
                background-color: #FAFAFA;
            }}
            /* Dark mode compatibility based on stream-lit container styling if possible */
            @media (prefers-color-scheme: dark) {{
                #network {{
                    background-color: #0E1117;
                    border: 1px solid rgba(255,255,255,0.1);
                }}
            }}
            body {{
                margin: 0;
                padding: 0;
                overflow: hidden;
            }}
        </style>
    </head>
    <body>
        <div id="network"></div>
        <script type="text/javascript">
            const nodes = new vis.DataSet({nodes_json});
            const edges = new vis.DataSet({edges_json});
            
            const container = document.getElementById('network');
            const data = {{
                nodes: nodes,
                edges: edges
            }};
            
            const options = {{
                nodes: {{
                    shape: 'box',
                    margin: 8,
                    borderWidth: 2,
                    shapeProperties: {{
                        borderRadius: 6
                    }},
                    font: {{
                        size: 13,
                        face: 'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif'
                    }}
                }},
                edges: {{
                    arrows: {{
                        to: {{
                            enabled: true,
                            scaleFactor: 0.8
                        }}
                    }},
                    smooth: {{
                        enabled: true,
                        type: 'cubicBezier',
                        roundness: 0.4
                    }},
                    font: {{
                        size: 10,
                        align: 'middle',
                        face: 'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif'
                    }}
                }},
                physics: {{
                    enabled: true,
                    solver: 'barnesHut',
                    barnesHut: {{
                        gravitationalConstant: -1500,
                        centralGravity: 0.2,
                        springLength: 95,
                        springConstant: 0.04,
                        damping: 0.09,
                        avoidOverlap: 0.1
                    }},
                    stabilization: {{
                        enabled: true,
                        iterations: 200,
                        fit: true
                    }}
                }},
                interaction: {{
                    hover: true,
                    zoomView: true,
                    dragView: true
                }}
            }};
            
            const network = new vis.Network(container, data, options);
        </script>
    </body>
    </html>
    """
    components.html(html_content, height=460)

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
                # Render interactive vis.js graph
                render_vis_network(graph_relations)
                
                # Render text list in an expander for accessibility
                with st.expander("Details (Text List)", expanded=False):
                    for rel in graph_relations:
                        if isinstance(rel, dict):
                            source = rel.get("source", "")
                            relation = rel.get("relation", "")
                            target = rel.get("target", "")
                        elif isinstance(rel, str):
                            parts = rel.split(" ", 2)
                            if len(parts) == 3:
                                source, relation, target = parts
                            else:
                                source, relation, target = rel, "", ""
                        else:
                            continue
                        c1, c2, c3 = st.columns([2, 2, 2])
                        c1.success(source)
                        c2.warning(f"──[{relation}]──▶")
                        c3.success(target)
            else:
                st.caption("No graph relationships matched the latest query.")
