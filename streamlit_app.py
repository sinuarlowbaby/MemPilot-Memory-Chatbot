import streamlit as st
import httpx
import uuid
import re

# Set page configuration
st.set_page_config(
    page_title="Mem0 Chatbot Studio",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling for premium look and feel
st.markdown("""
<style>
    /* Import Outfit Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Core App Background */
    .stApp {
        background-color: #0b0f19;
        color: #f3f4f6;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #0f172a !important;
        border-right: 1px solid #1e293b;
    }
    
    section[data-testid="stSidebar"] .stMarkdown {
        color: #94a3b8;
    }
    
    /* Main Layout Custom Header */
    .header-container {
        padding: 1.5rem;
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.6) 0%, rgba(30, 41, 59, 0.4) 100%);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 1.25rem;
        margin-bottom: 2rem;
        backdrop-filter: blur(12px);
        box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
    }
    
    .main-title {
        font-weight: 700;
        font-size: 2.25rem;
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 50%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    .subtitle {
        color: #94a3b8;
        font-size: 0.95rem;
        margin-top: 0.5rem;
        margin-bottom: 0;
    }
    
    /* Chat Message Bubbles */
    .chat-bubble {
        padding: 1rem 1.25rem;
        border-radius: 1rem;
        margin-bottom: 1rem;
        line-height: 1.5;
        font-size: 0.95rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        max-width: 85%;
        word-wrap: break-word;
    }
    
    .chat-user {
        background: linear-gradient(135deg, #1e1b4b 0%, #311042 100%);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-left: 4px solid #6366f1;
        margin-left: auto;
        color: #e0e7ff;
    }
    
    .chat-assistant {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-left: 4px solid #10b981;
        margin-right: auto;
        color: #f3f4f6;
    }
    
    .chat-sender {
        font-weight: 600;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.35rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .chat-sender-user {
        color: #818cf8;
    }
    
    .chat-sender-assistant {
        color: #34d399;
    }
    
    /* Memory Hub Styles */
    .memory-hub-container {
        background: rgba(15, 23, 42, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.05);
        padding: 1.25rem;
        border-radius: 1.25rem;
        height: calc(100vh - 180px);
        overflow-y: auto;
        backdrop-filter: blur(10px);
        box-shadow: inset 0 0 20px rgba(0, 0, 0, 0.2);
    }
    
    .memory-hub-title {
        font-weight: 700;
        font-size: 1.25rem;
        color: #ffffff;
        margin-bottom: 1.25rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        padding-bottom: 0.75rem;
    }
    
    .memory-section-title {
        font-size: 0.9rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #94a3b8;
        margin-top: 1.25rem;
        margin-bottom: 0.75rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Memory Cards */
    .memory-card {
        background: rgba(30, 41, 59, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.05);
        padding: 0.75rem 1rem;
        border-radius: 0.75rem;
        margin-bottom: 0.5rem;
        font-size: 0.875rem;
        color: #cbd5e1;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .memory-card:hover {
        border-color: rgba(99, 102, 241, 0.4);
        background: rgba(99, 102, 241, 0.05);
        transform: translateY(-2px);
    }
    
    .memory-card-vector {
        border-left: 3px solid #3b82f6;
    }
    
    .memory-card-graph {
        border-left: 3px solid #c084fc;
    }
    
    .memory-icon {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 1.5rem;
        height: 1.5rem;
        border-radius: 0.375rem;
        font-size: 0.85rem;
    }
    
    .memory-icon-vector {
        background-color: rgba(59, 130, 246, 0.15);
        color: #60a5fa;
    }
    
    .memory-icon-graph {
        background-color: rgba(192, 132, 252, 0.15);
        color: #d8b4fe;
    }
    
    .memory-text {
        flex-grow: 1;
        line-height: 1.4;
    }
    
    /* Graph Nodes Formatting */
    .graph-node {
        background: rgba(99, 102, 241, 0.15);
        border: 1px solid rgba(99, 102, 241, 0.25);
        color: #c7d2fe;
        padding: 0.15rem 0.5rem;
        border-radius: 0.375rem;
        font-weight: 500;
        font-size: 0.825rem;
    }
    
    .graph-edge {
        color: #f472b6;
        font-family: monospace;
        font-weight: 600;
        font-size: 0.75rem;
        padding: 0 0.25rem;
        letter-spacing: -0.05em;
    }
    
    .no-memory-placeholder {
        color: #64748b;
        font-style: italic;
        font-size: 0.85rem;
        padding: 1.25rem;
        text-align: center;
        background: rgba(30, 41, 59, 0.15);
        border: 1px dashed rgba(255, 255, 255, 0.05);
        border-radius: 0.75rem;
        margin-top: 0.5rem;
    }
    
    /* Input adjustments */
    div[data-baseweb="input"] {
        background-color: #1f2937 !important;
        border-color: #374151 !important;
    }
    
    /* Toggle switch styling override */
    .stCheckbox > label {
        color: #d1d5db !important;
    }
    
    /* Status Badge */
    .status-badge {
        font-size: 0.7rem;
        padding: 0.15rem 0.5rem;
        border-radius: 9999px;
        font-weight: 600;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        display: inline-flex;
        align-items: center;
    }
    
    .status-cache-hit {
        background-color: rgba(16, 185, 129, 0.15);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.25);
    }
    
    .status-cache-miss {
        background-color: rgba(245, 158, 11, 0.15);
        color: #fbbf24;
        border: 1px solid rgba(245, 158, 11, 0.25);
    }
</style>
""", unsafe_allow_html=True)

# Helper function to format Graph relations beautifully
def format_graph_relation(rel_str: str) -> str:
    parts = rel_str.split(" ", 2)
    if len(parts) >= 3:
        source, relation, target = parts[0], parts[1], parts[2]
        return f'<span class="graph-node">{source}</span><span class="graph-edge"> ──[{relation}]──&gt; </span><span class="graph-node">{target}</span>'
    return f'<span class="memory-text">{rel_str}</span>'

# Initialize session state variables
if "session_id" not in st.session_state:
    st.session_state.session_id = f"user-{str(uuid.uuid4())[:8]}"
if "messages" not in st.session_state:
    st.session_state.messages = []
if "show_memory" not in st.session_state:
    st.session_state.show_memory = True

# --- SIDEBAR CONFIGURATION ---
with st.sidebar:
    st.image("https://raw.githubusercontent.com/mem0ai/mem0/main/docs/images/mem0-logo.png", width=120)
    st.markdown("### **Config Studio**")
    st.markdown("Tailor the execution settings below.")
    
    # Model Selection
    selected_model = st.selectbox(
        "AI Model Name",
        options=["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"],
        index=0,
        help="Select the OpenAI foundation model to power the chat response."
    )
    
    # Session ID Input
    user_session_id = st.text_input(
        "User ID (Session ID)",
        value=st.session_state.session_id,
        help="The unique identifier to store and retrieve personal episodic memories."
    )
    # Sync user ID back to session state
    if user_session_id != st.session_state.session_id:
        st.session_state.session_id = user_session_id
        st.session_state.messages = []  # Reset message buffer for new session
        st.rerun()
        
    # Togglable Memory View on Side
    show_memory_panel = st.toggle(
        "Show Memory Hub Panel",
        value=st.session_state.show_memory,
        help="Split screen to show retrieved vector and graph memories on the side."
    )
    st.session_state.show_memory = show_memory_panel
    
    st.markdown("---")
    
    # Actions
    if st.button("Reset Chat Buffer", use_container_width=True):
        st.session_state.messages = []
        st.success("Chat history cleared!")
        st.rerun()

# --- MAIN INTERFACE LAYOUT ---
# Header
st.markdown("""
<div class="header-container">
    <div class="main-title">🧠 Mem0 Chatbot Studio</div>
    <div class="subtitle">A premium FastAPI interface rendering hybrid semantic vectors & Neo4j graph relationships in real-time.</div>
</div>
""", unsafe_allow_html=True)

# Layout Columns
if st.session_state.show_memory:
    col_chat, col_memory = st.columns([7, 5], gap="large")
else:
    col_chat = st.container()
    col_memory = None

# --- CHAT WORKFLOW ---
with col_chat:
    st.markdown("<h4 style='margin-bottom: 1.25rem; font-weight:600; color:#e2e8f0;'>Conversation History</h4>", unsafe_allow_html=True)
    
    # Scrollable chat box
    chat_container = st.container()
    
    with chat_container:
        # Display existing messages
        for msg in st.session_state.messages:
            sender_class = "chat-user" if msg["role"] == "user" else "chat-assistant"
            sender_label = "You" if msg["role"] == "user" else "Assistant"
            label_class = "chat-sender-user" if msg["role"] == "user" else "chat-sender-assistant"
            
            # Badge for Cache Hit
            badge_html = ""
            if msg["role"] == "assistant":
                if msg.get("cache_hit"):
                    badge_html = ' <span class="status-badge status-cache-hit">Cache Hit</span>'
                else:
                    badge_html = ' <span class="status-badge status-cache-miss">Cache Miss</span>'
            
            st.markdown(f"""
            <div class="chat-bubble {sender_class}">
                <div class="chat-sender {label_class}">
                    <span>{sender_label}</span>
                    {badge_html}
                </div>
                <div>{msg["content"]}</div>
            </div>
            """, unsafe_allow_html=True)
            
    # Chat Input
    if prompt := st.chat_input("Enter your message..."):
        # Display user message instantly
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Call backend FastAPI service
        backend_url = "http://localhost:8000/chat"
        payload = {
            "user_query": prompt,
            "session_id": st.session_state.session_id,
            "model": selected_model
        }
        
        try:
            with st.spinner("Analyzing context & generating response..."):
                response = httpx.post(backend_url, json=payload, timeout=30.0)
                
            if response.status_code == 200:
                data = response.json()
                ai_reply = data.get("response", "")
                cache_hit = data.get("cache_hit", False)
                memories = data.get("memories", [])
                graph_relations = data.get("graph_relations", [])
                
                # Append assistant reply to message history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": ai_reply,
                    "cache_hit": cache_hit,
                    "memories": memories,
                    "graph_relations": graph_relations
                })
                
                # Rerun to refresh views
                st.rerun()
            else:
                st.error(f"Error calling backend: API returned status code {response.status_code}")
                st.markdown(f"**Details:** `{response.text}`")
        except Exception as e:
            st.error("Failed to connect to the FastAPI backend.")
            st.info("Please ensure the FastAPI service is running locally on port 8000: `python -m app.main` or `uvicorn app.main:app --reload`")
            st.warning(f"Technical error: {e}")

# --- MEMORY HUB SIDE PANEL ---
if col_memory is not None:
    with col_memory:
        # Determine the latest assistant message to fetch current memories
        last_assistant_msg = None
        for msg in reversed(st.session_state.messages):
            if msg["role"] == "assistant":
                last_assistant_msg = msg
                break
                
        # Card container
        st.markdown('<div class="memory-hub-container">', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="memory-hub-title">
            <span>🧠 Memory Hub</span>
        </div>
        """, unsafe_allow_html=True)
        
        # 1. Semantic Vector Memories
        st.markdown("""
        <div class="memory-section-title">
            <span>🔹 Semantic Vector Memories (Mem0)</span>
        </div>
        """, unsafe_allow_html=True)
        
        if last_assistant_msg and last_assistant_msg.get("memories"):
            for idx, mem in enumerate(last_assistant_msg["memories"]):
                # Extract text depending on dict or string shape
                mem_text = mem.get("memory", "") if isinstance(mem, dict) else str(mem)
                if not mem_text:
                    continue
                st.markdown(f"""
                <div class="memory-card memory-card-vector">
                    <div class="memory-icon memory-icon-vector">{idx+1}</div>
                    <div class="memory-text">{mem_text}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown('<div class="no-memory-placeholder">No semantic vector memories retrieved for the current turn.</div>', unsafe_allow_html=True)
            
        # 2. Neo4j Graph Relationships
        st.markdown("""
        <div class="memory-section-title">
            <span>🔮 Graph Knowledge Relationships (Neo4j)</span>
        </div>
        """, unsafe_allow_html=True)
        
        if last_assistant_msg and last_assistant_msg.get("graph_relations"):
            for idx, rel in enumerate(last_assistant_msg["graph_relations"]):
                formatted_rel = format_graph_relation(rel)
                st.markdown(f"""
                <div class="memory-card memory-card-graph">
                    <div class="memory-icon memory-icon-graph">🔗</div>
                    <div class="memory-text">{formatted_rel}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown('<div class="no-memory-placeholder">No knowledge graph relationships matched the current query.</div>', unsafe_allow_html=True)
            
        st.markdown('</div>', unsafe_allow_html=True)
