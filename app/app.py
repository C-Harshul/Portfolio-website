"""Streamlit frontend for Portfolio Website Chat Interface."""

import streamlit as st
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag.chain import build_rag_chain
from ingestion.embeddings import CFWorkersAIEmbeddings, CLOUDFLARE_ACCOUNT_ID, CLOUDFLARE_API_TOKEN, CF_EMBEDDINGS_MODEL
from config.settings import GOOGLE_API_KEY

# Configure Streamlit page
st.set_page_config(
    page_title="Harshul Chandrashekhar",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for elegant chat UI
st.markdown("""
<style>
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Full height layout */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 900px;
        height: 100vh;
        display: flex;
        flex-direction: column;
    }
    
    /* Header styling */
    .chat-header {
        padding: 1.5rem 0;
        border-bottom: 1px solid rgba(0, 0, 0, 0.08);
        margin-bottom: 1rem;
    }
    
    .chat-header h1 {
        font-size: 1.75rem;
        font-weight: 600;
        margin: 0;
        color: #1a1a1a;
        letter-spacing: -0.02em;
    }
    
    .chat-header p {
        font-size: 0.95rem;
        color: #666;
        margin: 0.25rem 0 0 0;
        font-weight: 400;
    }
    
    /* Chat container */
    .chat-container {
        flex: 1;
        overflow-y: auto;
        padding: 1rem 0;
        margin-bottom: 1rem;
    }
    
    /* Message bubbles */
    .stChatMessage {
        padding: 0.75rem 0;
        animation: fadeIn 0.3s ease-in;
    }
    
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(4px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* User message styling */
    .stChatMessage[data-testid="user-message"] {
        background: transparent;
    }
    
    .stChatMessage[data-testid="user-message"] .stChatMessageContent {
        background: #f5f5f5;
        border-radius: 18px;
        padding: 0.875rem 1.125rem;
        margin-left: auto;
        max-width: 75%;
        border: 1px solid rgba(0, 0, 0, 0.05);
    }
    
    /* Assistant message styling */
    .stChatMessage[data-testid="assistant-message"] {
        background: transparent;
    }
    
    .stChatMessage[data-testid="assistant-message"] .stChatMessageContent {
        background: #ffffff;
        border-radius: 18px;
        padding: 0.875rem 1.125rem;
        margin-right: auto;
        max-width: 75%;
        border: 1px solid rgba(0, 0, 0, 0.08);
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
    }
    
    /* Typography */
    .stChatMessageContent p {
        margin: 0;
        line-height: 1.6;
        font-size: 0.95rem;
        color: #1a1a1a;
    }
    
    .stChatMessageContent ul, .stChatMessageContent ol {
        margin: 0.5rem 0;
        padding-left: 1.25rem;
    }
    
    /* Input area */
    .chat-input-container {
        padding-top: 1rem;
        border-top: 1px solid rgba(0, 0, 0, 0.08);
    }
    
    /* Example prompts */
    .example-prompts {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin-bottom: 0.75rem;
    }
    
    .prompt-chip {
        background: #f8f8f8;
        border: 1px solid rgba(0, 0, 0, 0.08);
        border-radius: 12px;
        padding: 0.5rem 0.875rem;
        font-size: 0.85rem;
        color: #555;
        cursor: pointer;
        transition: all 0.2s ease;
        font-weight: 400;
    }
    
    .prompt-chip:hover {
        background: #f0f0f0;
        border-color: rgba(0, 0, 0, 0.12);
        transform: translateY(-1px);
    }
    
    /* Typing indicator */
    .typing-indicator {
        display: flex;
        gap: 0.4rem;
        padding: 0.875rem 1.125rem;
        background: #ffffff;
        border-radius: 18px;
        border: 1px solid rgba(0, 0, 0, 0.08);
        max-width: 75px;
        margin-right: auto;
    }
    
    .typing-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: #999;
        animation: typing 1.4s infinite;
    }
    
    .typing-dot:nth-child(2) {
        animation-delay: 0.2s;
    }
    
    .typing-dot:nth-child(3) {
        animation-delay: 0.4s;
    }
    
    @keyframes typing {
        0%, 60%, 100% {
            transform: translateY(0);
            opacity: 0.5;
        }
        30% {
            transform: translateY(-4px);
            opacity: 1;
        }
    }
    
    /* Dark mode support */
    @media (prefers-color-scheme: dark) {
        .chat-header h1 {
            color: #f5f5f5;
        }
        
        .chat-header p {
            color: #999;
        }
        
        .chat-header {
            border-bottom-color: rgba(255, 255, 255, 0.1);
        }
        
        .stChatMessage[data-testid="user-message"] .stChatMessageContent {
            background: #2a2a2a;
            border-color: rgba(255, 255, 255, 0.1);
        }
        
        .stChatMessage[data-testid="assistant-message"] .stChatMessageContent {
            background: #1a1a1a;
            border-color: rgba(255, 255, 255, 0.1);
        }
        
        .stChatMessageContent p {
            color: #e5e5e5;
        }
        
        .chat-input-container {
            border-top-color: rgba(255, 255, 255, 0.1);
        }
        
        .prompt-chip {
            background: #2a2a2a;
            border-color: rgba(255, 255, 255, 0.1);
            color: #ccc;
        }
        
        .prompt-chip:hover {
            background: #333;
        }
        
        .typing-indicator {
            background: #1a1a1a;
            border-color: rgba(255, 255, 255, 0.1);
        }
        
        .typing-dot {
            background: #999;
        }
    }
    
    /* Scrollbar styling */
    .chat-container::-webkit-scrollbar {
        width: 6px;
    }
    
    .chat-container::-webkit-scrollbar-track {
        background: transparent;
    }
    
    .chat-container::-webkit-scrollbar-thumb {
        background: rgba(0, 0, 0, 0.2);
        border-radius: 3px;
    }
    
    .chat-container::-webkit-scrollbar-thumb:hover {
        background: rgba(0, 0, 0, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# Check if required environment variables are set
if not GOOGLE_API_KEY:
    st.error("Please set GOOGLE_API_KEY in your environment variables.")
    st.stop()

# Initialize RAG chain function
def initialize_rag_chain(force_refresh=True):
    """
    Initialize the RAG chain with completely fresh components.
    
    Args:
        force_refresh: If True, forces a fresh connection to ChromaDB to avoid caching (default: True)
    """
    try:
        # Create a completely fresh embedding client for each query
        fresh_embedder = CFWorkersAIEmbeddings(
            account_id=CLOUDFLARE_ACCOUNT_ID,
            api_token=CLOUDFLARE_API_TOKEN,
            model=CF_EMBEDDINGS_MODEL
        )
        # Force refresh to ensure we get the latest data from ChromaDB
        return build_rag_chain(fresh_embedder, force_refresh=force_refresh)
    except Exception as e:
        st.error(f"Failed to initialize RAG chain: {str(e)}")
        return None

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

if "is_processing" not in st.session_state:
    st.session_state.is_processing = False

# Header
st.markdown("""
<div class="chat-header">
    <h1>Harshul Chandrashekhar</h1>
    <p>Ask me anything about my experience, projects, or background</p>
</div>
""", unsafe_allow_html=True)

# Chat container
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Show typing indicator if processing
if st.session_state.is_processing and st.session_state.messages:
    last_msg = st.session_state.messages[-1]
    if last_msg["role"] == "user":
        st.markdown("""
        <div class="typing-indicator">
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        </div>
        """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Chat input
st.markdown('<div class="chat-input-container">', unsafe_allow_html=True)

# Example prompts (only show if no messages yet)
if len(st.session_state.messages) == 0:
    example_prompts = [
        "Tell me about your background",
        "What projects have you worked on?",
        "What are your technical skills?",
        "What's your experience with AI/ML?"
    ]
    
    cols = st.columns(4)
    for i, prompt in enumerate(example_prompts):
        with cols[i]:
            if st.button(prompt, key=f"prompt_{i}", use_container_width=True):
                user_input = prompt
                st.session_state.messages.append({"role": "user", "content": user_input})
                st.rerun()

# Get user input
user_input = st.chat_input("Type your message...")

st.markdown('</div>', unsafe_allow_html=True)

# Process user input
if user_input:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.rerun()

# Process the query if we have a new user message waiting for response
if st.session_state.messages:
    last_message = st.session_state.messages[-1]
    # Check if last message is from user and we haven't responded yet
    if last_message["role"] == "user" and not st.session_state.is_processing:
        # Set processing state
        st.session_state.is_processing = True
        st.rerun()
    
    # Process the query
    if st.session_state.is_processing and last_message["role"] == "user":
        try:
            # Build fresh chain on each query to get latest data
            rag_chain = initialize_rag_chain()
            if rag_chain is None:
                response = "Failed to initialize the system. Please check your configuration."
            else:
                response = rag_chain.invoke(last_message["content"])
            
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
        finally:
            st.session_state.is_processing = False
            st.rerun()

if __name__ == "__main__":
    pass
