import sys
import os
import requests
import argparse
import json
from dotenv import load_dotenv
from groq_mcp_client import GroqClient

# Load environment variables from .env file
load_dotenv()

def check_mcp_server():
    mcp_url = os.environ.get("MCP_SERVER_URL", "http://localhost:8000")
    try:
        response = requests.get(f"{mcp_url}/health", timeout=2)
        if response.status_code == 200:
            return True
        return False
    except requests.exceptions.RequestException:
        return False
    
def main():
    parser = argparse.ArgumentParser(description="Ask Groq questions with web search capability")
    parser.add_argument("query", nargs="*", help="the question to ask Groq")
    args = parser.parse_args()

    if not os.environ.get("GROQ_API_KEY"):
        print("Error: GROQ_API_KEY environment variable is required")
        print("Please set it in your .env file or environment variables")
        sys.exit(1)

    if args.query:
        query = " ".join(args.query)
    else:
        query = input("Ask Groq: ")
    
    client = GroqClient()

    print(f"Searching for: {query}")

    try:
        answer = client.get_final_answer(query)
        print("Answer:", answer)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main() 