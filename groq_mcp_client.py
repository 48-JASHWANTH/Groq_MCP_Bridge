import os
import json
import requests
import time
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

GROQ_API_KEY = os.environ.get("GROQ_API_KEY","")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
MCP_SERVER_URL = os.environ.get("MCP_SERVER_URL","http://localhost:8000")


class GroqClient:
    def __init__(self, api_key: str = GROQ_API_KEY, model: str = "llama3-70b-8192"):
        self.api_key = api_key
        self.model = model
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        self.tools = [{
            "type": "function",
            "function": {
                "name": "fetch_web_content",
                "description": "Retrieves info from website based on user queries",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query or website to look up information about"
                        }
                    },
                    "required": ["query"]
                }
            }
        }]

        self._check_mcp_server()

    def _check_mcp_server(self):
        try:
            response = requests.get(f"{MCP_SERVER_URL}/health", timeout=2)
            if response.status_code == 200:
                return True
        except:
            pass
        return False
    
    def send_message(self, message: str, conversation_history: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        if not self.api_key:
            raise ValueError("API Key of Groq is required....")
        if conversation_history is None:
            conversation_history = []

        # Convert conversation history to OpenAI format
        messages = conversation_history + [{"role": "user", "content": message}]

        payload = {
            "model": self.model,
            "messages": messages,
            "tools": self.tools,
            "tool_choice": "auto",
            "max_tokens": 4096
        }

        print("Sending request to Groq...")
        try:
            response = requests.post(
                GROQ_API_URL,
                headers=self.headers,
                json=payload
            )

            if response.status_code != 200:
                print(response.text)
                print("Error")
            
            response.raise_for_status()

            result = response.json()
            print(f"Groq response: {result}")

            has_tool_call = False
            tool_call = {}

            if "choices" in result and result["choices"]:
                choice = result["choices"][0]
                if "message" in choice and "tool_calls" in choice["message"]:
                    has_tool_call = True
                    print("Tool call detected")
                    
                    for tool_call_obj in choice["message"]["tool_calls"]:
                        tool_call["name"] = tool_call_obj["function"]["name"]
                        tool_call["parameters"] = json.loads(tool_call_obj["function"]["arguments"])
                        print(f"Tool call details: {tool_call}")

                        tool_response = self._handle_tool_call(tool_call)
                        print(f"Tool response: {tool_response}")

                        # Add the assistant's message with tool call
                        conversation_history.append({"role": "user", "content": message})
                        conversation_history.append(choice["message"])

                        # Add tool response
                        conversation_history.append({
                            "role": "tool",
                            "tool_call_id": tool_call_obj["id"],
                            "content": json.dumps(tool_response)
                        })

                        # Changed this prompt to be more direct and avoid mentioning tool calls
                        return self.send_message("Please answer the original query based on available information.", conversation_history)

            if not has_tool_call:
                print("No tool calls")

            return result
        except Exception as e:
            print(e)

    def _handle_tool_call(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        tool_name = tool_call.get("name")
        tool_params = tool_call.get("parameters")

        if not self._check_mcp_server():
            return {
                "error": "MCP server not available"
            }
        
        max_retries = 3
        retry_count = 0

        while retry_count < max_retries:
            try:
                response = requests.post(
                    f"{MCP_SERVER_URL}/tool_call",
                    json={"name": tool_name, "parameters": tool_params},
                    timeout=10
                )
                response.raise_for_status()
                return response.json()
            
            except Exception as e:
                retry_count += 1
                if retry_count < max_retries:
                    wait_time = 2 ** retry_count
                    time.sleep(wait_time)
                else:
                    return {
                        "error": "MCP server not responding..."
                    }
                
    def get_final_answer(self, message: str) -> str:
        try:
            response = self.send_message(message)

            if "choices" in response and response["choices"]:
                choice = response["choices"][0]
                if "message" in choice and "content" in choice["message"]:
                    return choice["message"]["content"]
            return "No clear answer found..."
        except Exception as e:
            return f"Error: {e}" 