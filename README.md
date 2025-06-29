# MCP Project with Groq Integration

This project provides a Model Context Protocol (MCP) server that integrates with Groq's API for AI-powered web search capabilities.

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set environment variables:**
   
   Create a `.env` file in the project root with the following content:
   ```
   # Groq API key (required)
   GROQ_API_KEY=your_groq_api_key_here
   
   # MCP server URL (optional, defaults to http://localhost:8000)
   MCP_SERVER_URL=http://localhost:8000
   
   # Port for Flask server (optional, defaults to 8000)
   PORT=8000
   ```
   
   Alternatively, you can set these environment variables directly:
   ```bash
   export GROQ_API_KEY="your_groq_api_key_here"
   export MCP_SERVER_URL="http://localhost:8000"  # Optional, defaults to localhost:8000
   ```

3. **Start the MCP server:**
   ```bash
   python mcp_server.py
   ```

4. **Use the application:**

   **Option 1: Web Interface (Streamlit)**
   ```bash
   streamlit run app.py
   ```
   This will start a web server and open the application in your default browser.

   **Option 2: Command Line**
   ```bash
   python ask_groq.py "What is the latest news about AI?"
   ```

## Available Models

Groq supports various models including:
- `llama3-70b-8192` (default)
- `mixtral-8x7b-32768`
- `gemma2-9b-it`
- `llama3-8b-8192`

You can change the model in `groq_mcp_client.py` by modifying the `model` parameter in the `GroqClient` constructor.

## Features

- Web search integration via DuckDuckGo API
- Tool calling for enhanced functionality
- Conversation history support
- Automatic retry logic for failed requests
- Health check endpoints
- Streamlit web interface with:
  - Real-time system status monitoring
  - Conversation history
  - Clear conversation button
  - Responsive layout
- Environment variable support through .env file

## Files

- `groq_mcp_client.py`: Main Groq client implementation
- `ask_groq.py`: Command-line interface for asking questions
- `mcp_server.py`: Flask server for handling tool calls
- `mcp_integration.py`: Integration layer for web search functionality
- `app.py`: Streamlit web application
- `.env`: Environment variables configuration (create this file) 
