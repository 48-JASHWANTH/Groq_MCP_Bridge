import os
import re
import json 
import requests
from typing import Dict, List, Any, Optional, Literal
from dataclasses import dataclass, asdict
import openai

DUCKDUCKGO_ENDPOINT = "https://api.duckduckgo.com"
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

LLMProvider = Literal["groq"]

@dataclass
class DDGRequest:
    q: str
    format: str = "json"
    no_html: int = 1
    skip_disambig: int = 1

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass  
class WebResult:
    title: str
    url: str
    description: str

class MCPClient:
    def __init__(self, endpoint: str = DUCKDUCKGO_ENDPOINT):
        self.endpoint = endpoint
    
    def search(self, query: str, count: int = 10) -> List[WebResult]:
        request = DDGRequest(q=query)

        try:
            response = requests.get(
                self.endpoint,
                params=request.to_dict()
            )

            response.raise_for_status()

            data = response.json()
            results = []

            if data.get("Abstract"):
                results.append(WebResult(
                    title=data.get("Heading", ""),
                    url=data.get("AbstractURL", ""),
                    description=data.get("Abstract", "")
                ))
            return results
        except Exception as e:
            print(e)
            return []

class GroqMCPBridge:

    def __init__(self, llm_provider: LLMProvider = "groq"):
        self.mcp_client = MCPClient()
        self.llm_provider = llm_provider

        if llm_provider == "groq":
            # Use the Groq API directly with requests instead of OpenAI client
            self.groq_api_key = GROQ_API_KEY
            self.groq_api_url = "https://api.groq.com/openai/v1/chat/completions"

    def extract_website_queries_with_llm(self, user_message: str) -> List[str]:
        if self.llm_provider == "groq":
            return self._extract_with_groq(user_message)
        else:
            return ["error"]
    
    def _extract_with_groq(self, user_message: str) -> List[str]:
        try:
            headers = {
                "Authorization": f"Bearer {self.groq_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "llama3-70b-8192",
                "messages": [
                    {"role": "system", "content": "You are helpful assistant that identifies web search queries in user message. Extract any specific website or topic queries the user wants information about. Return results as a JSON object with a 'queries' field containing an array of strings. If no queries are found, return an empty array."},
                    {"role": "user", "content": user_message}
                ],
                "max_tokens": 1000,
                "temperature": 0.1
            }

            response = requests.post(
                self.groq_api_url,
                headers=headers,
                json=payload
            )
            response.raise_for_status()

            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            json_match = re.search(r'```(?:json)?\s*({.*?})\s*```', content, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group(1))
            else:
                try:
                    result = json.loads(content)
                except:
                    return ["error"]
            queries = result.get("queries", [])
            return queries
        
        except Exception as e:
            print(e)
            return []

def handle_groq_tool_call(tool_params: Dict[str, Any]) -> Dict[str, Any]:
    query = tool_params.get("query", "")
    if not query:
        return {"error": "no query"}
    
    bridge = GroqMCPBridge()
    results = bridge.mcp_client.search(query)

    return {
        "results": [asdict(result) for result in results]
    }