import streamlit as st
import os
import sys
import requests
from groq_mcp_client import GroqClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set page configuration
st.set_page_config(
    page_title="Groq MCP Query App",
    page_icon="🤖",
    layout="wide"
)

def check_api_key():
    """Check if the GROQ_API_KEY is set"""
    api_key = os.environ.get("GROQ_API_KEY")
    return api_key is not None and api_key != ""

def check_mcp_server():
    """Check if the MCP server is running"""
    mcp_url = os.environ.get("MCP_SERVER_URL", "http://localhost:8000")
    try:
        response = requests.get(f"{mcp_url}/health", timeout=2)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def update_messages_list():
    """Convert session state conversations to format expected by Groq client"""
    messages = []
    for msg in st.session_state.conversation_history:
        if msg["role"] in ["user", "assistant", "system"]:
            messages.append({"role": msg["role"], "content": msg["content"]})
    return messages

# Initialize session state for conversation history
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []
    # Add system message to set context
    st.session_state.conversation_history.append({
        "role": "system", 
        "content": "You are a helpful assistant powered by Groq. You can search the web when needed to provide accurate and up-to-date information."
    })

# App header with custom styling
st.markdown("""
    <style>
    .main-header {
        text-align: center;
        background-color: #1E1E1E;
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header"><h1>Groq MCP Query Application</h1></div>', unsafe_allow_html=True)

# Main layout
col1, col2 = st.columns([3, 1])

with col1:
    # Chat container
    st.markdown("<h3>Chat Interface</h3>", unsafe_allow_html=True)
    
    # Display conversation history (skip system message)
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.conversation_history:
            if message["role"] == "user":
                st.chat_message("user").write(message["content"])
            elif message["role"] == "assistant":
                st.chat_message("assistant").write(message["content"])
    
    # Query input
    query = st.chat_input("Ask a question...")
    
    if query:
        # Display user message
        st.chat_message("user").write(query)
        
        # Add user message to history
        st.session_state.conversation_history.append({"role": "user", "content": query})
        
        # Show processing message
        with st.spinner("Processing your query..."):
            # Check if we can proceed
            if not check_api_key():
                response = "Cannot process query. GROQ_API_KEY not found in .env file or environment variables."
            elif not check_mcp_server():
                response = "Cannot process query. MCP server is not running. Run 'python mcp_server.py' first."
            else:
                try:
                    # Create client and get response with conversation history
                    client = GroqClient()
                    messages = update_messages_list()
                    
                    # Remove the latest user message as it's passed separately
                    conversation_context = messages[:-1] if len(messages) > 1 else []
                    
                    # Send query with conversation context
                    result = client.send_message(query, conversation_context)
                    
                    if "choices" in result and result["choices"]:
                        choice = result["choices"][0]
                        if "message" in choice and "content" in choice["message"]:
                            response = choice["message"]["content"]
                        else:
                            response = "No clear answer found..."
                    else:
                        response = "No response from Groq API"
                except Exception as e:
                    response = f"Error: {str(e)}"
        
        # Display assistant response
        st.chat_message("assistant").write(response)
        
        # Add assistant response to history
        st.session_state.conversation_history.append({"role": "assistant", "content": response})
        
        # Rerun to update the display
        st.rerun()

with col2:
    # Sidebar for status and configuration
    st.markdown("<h3>System Status</h3>", unsafe_allow_html=True)
    
    # Check API key
    if check_api_key():
        st.success("✅ GROQ API Key found")
    else:
        st.error("❌ GROQ API Key not found")
        st.info("Set your GROQ_API_KEY in .env file or environment variables")
    
    # Check MCP server
    if check_mcp_server():
        st.success("✅ MCP Server is running")
    else:
        st.error("❌ MCP Server is not running")
        st.info("Start the MCP server using 'python mcp_server.py'")
    
    # Controls
    st.markdown("<h3>Controls</h3>", unsafe_allow_html=True)
    
    if st.button("Clear Conversation"):
        # Reset conversation but keep system message
        system_message = next((msg for msg in st.session_state.conversation_history if msg["role"] == "system"), None)
        st.session_state.conversation_history = [system_message] if system_message else []
        st.rerun()
    
    st.markdown("<h3>About</h3>", unsafe_allow_html=True)
    st.markdown("""
    This app integrates with Groq's API for AI-powered web search capabilities.
    
    Ask any question and the system will utilize web search when needed to provide 
    accurate and up-to-date information.
    
    **Features:**
    - Web search integration
    - Conversation history
    - Real-time status monitoring
    """)

# Footer
st.markdown("---")
st.caption("Powered by Groq and DuckDuckGo") 