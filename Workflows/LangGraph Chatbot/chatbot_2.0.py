import streamlit as st
from langgraph_backend import chatbot
from langchain_core.messages import BaseMessage, HumanMessage

# --- Page Configuration ---
st.set_page_config(
    page_title="GenAI Assistant",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- Advanced Styling (CSS) ---
st.markdown("""
<style>
    /* Import modern font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Hide standard Streamlit header/footer/menu for immersion */
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}

    /* Main Container Padding */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 5rem !important;
        max-width: 800px;
    }

    /* Hero Section Styling */
    .hero-container {
        text-align: center;
        padding: 5rem 0;
        animation: fadeIn 1.2s ease-in-out;
    }
    
    .hero-title {
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .hero-subtitle {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }

    /* Chat Message Polish */
    .stChatMessage {
        background-color: transparent;
        border: none;
    }
    
    .stChatMessage .stMarkdown {
        background: #f0f2f6;
        padding: 12px 16px;
        border-radius: 12px;
        color: #31333F;
    }
    
    /* Differentiate Assistant Bubble */
    div[data-testid="stChatMessage"]:nth-child(even) .stMarkdown {
         background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
         box-shadow: 0 2px 5px rgba(0,0,0,0.05);
         border: 1px solid #e0e0e0;
    }
    
    /* Dark mode override for specific elements if needed */
    @media (prefers-color-scheme: dark) {
        .stChatMessage .stMarkdown {
            background: #262730;
            color: #FAFAFA;
        }
        div[data-testid="stChatMessage"]:nth-child(even) .stMarkdown {
            background: #1E1E1E;
            border: 1px solid #444;
        }
        .hero-subtitle { color: #aaa; }
    }

    /* Input Field Styling */
    .stChatInput {
        position: fixed;
        bottom: 30px;
        z-index: 1000;
    }

    @keyframes fadeIn {
        0% { opacity: 0; transform: translateY(20px); }
        100% { opacity: 1; transform: translateY(0); }
    }
</style>
""", unsafe_allow_html=True)

# --- Sidebar Management ---
with st.sidebar:
    st.markdown("### ⚙️ Control Panel")
    st.write("Manage your conversation session.")
    st.divider()
    
    st.caption(f"Session ID: `1`")
    
    if st.button("✨ New Chat", use_container_width=True, type="primary"):
        st.session_state['message_history'] = []
        st.rerun()
        
    st.markdown("---")
    st.info("💡 **Tip:** Ask complex questions. I can handle context from previous messages.")

# --- State Initialization ---
thread_id = '1'
CONFIG = {'configurable': {'thread_id': thread_id}}

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

# --- Main Logic ---

# 1. Create a placeholder for the Hero section
hero_placeholder = st.empty()

# 2. Display Hero ONLY if history is empty
if not st.session_state['message_history']:
    with hero_placeholder.container():
        st.markdown("""
        <div class="hero-container">
            <div class="hero-title">Hello, there.</div>
            <div class="hero-subtitle">I'm your AI assistant. How can I help you achieve your goals today?</div>
        </div>
        """, unsafe_allow_html=True)

# 3. Render Existing Chat History
for message in st.session_state['message_history']:
    role = message['role']
    avatar = "https://api.dicebear.com/9.x/notionists/svg?seed=Felix" if role == 'user' else "https://api.dicebear.com/9.x/bottts-neutral/svg?seed=Aneka"
    with st.chat_message(role, avatar=avatar):
        st.markdown(message['content'])

# 4. Input Handling
user_input = st.chat_input('Message AI Assistant...')

if user_input:
    # A. Clear the Hero section immediately
    hero_placeholder.empty()

    # B. Add & Display User Message
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    with st.chat_message('user', avatar="https://api.dicebear.com/9.x/notionists/svg?seed=Felix"):
        st.markdown(user_input)

    # C. Generate & Display Assistant Response
    with st.chat_message('assistant', avatar="https://api.dicebear.com/9.x/bottts-neutral/svg?seed=Aneka"):
        with st.spinner("Thinking..."):
            try:
               
                ai_message = st.write_stream(message_chunk.content for message_chunk, metadata in  chatbot.stream(
                    {'messages': [HumanMessage(content=user_input)]}, 
                    config=CONFIG,
                    stream_mode='messages'
                    )
                )
                
                # Display and Save
                # st.markdown(ai_message)
                st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})
            except Exception as e:
                st.error(f"Something went wrong: {str(e)}")