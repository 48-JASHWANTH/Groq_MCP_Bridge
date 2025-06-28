import os
import json
from flask import Flask, request, jsonify
from mcp_integration import GroqMCPBridge, handle_groq_tool_call
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

PORT = int(os.environ.get("PORT", 8000))

app = Flask(__name__)
bridge = GroqMCPBridge()

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok"})

@app.route("/", methods=["GET"])
def root():
    return jsonify({
        "name": "MCP server",
        "status": "running",
        "endpoints": [
            {"path": "/health", "methods": ["GET"], "description": "health"},
            {"path": "/tool_call", "methods": ["POST"], "description": "Handle the tool call..."}
        ]
    })

@app.route("/tool_call", methods=["POST"])
def tool_call():
    if not request.json:
        return jsonify({"error": "invalid request"}), 400
    
    tool_name = request.json.get("name")
    parameters = request.json.get("parameters", {})

    if tool_name != "fetch_web_content":
        return jsonify({"error": "unknown tool name"}), 400
    
    result = handle_groq_tool_call(parameters)
    return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)