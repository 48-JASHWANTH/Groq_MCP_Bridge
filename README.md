# MCP Project with Groq Integration

This project provides a Model Context Protocol (MCP) server that integrates with Groq's API for AI-powered web search capabilities.

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set environment variables:**
   ```bash
   export GROQ_API_KEY="your_groq_api_key_here"
   export MCP_SERVER_URL="http://localhost:8000"  # Optional, defaults to localhost:8000
   ```

3. **Start the MCP server:**
   ```bash
   python mcp_server.py
   ```

4. **Ask questions using Groq:**
   ```bash
   python ask_groq.py "What is the latest news about AI?"
   ```

## Key Changes from Claude Version

- **API Integration**: Uses Groq's OpenAI-compatible API instead of Anthropic's Claude API
- **Models**: Uses Groq models like `llama3-70b-8192` or `mixtral-8x7b-32768`
- **Environment Variable**: Uses `GROQ_API_KEY` instead of `CLAUDE_API_KEY`
- **Tool Calling**: Updated to use OpenAI-compatible tool calling format

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

## Files

- `groq_mcp_client.py`: Main Groq client implementation
- `ask_groq.py`: Command-line interface for asking questions
- `mcp_server.py`: Flask server for handling tool calls
- `mcp_integration.py`: Integration layer for web search functionality 