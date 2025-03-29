import requests
import json
import logging
from typing import List, Dict, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MentalHealthAssistant:
    def __init__(self):
        self.ollama_url = "http://localhost:11434/api/chat"
        self.model = "gemma:2b"
        self.timeout = 30  # Increased timeout
        self.max_retries = 2

    def generate_response(self, user_input: str, history: Optional[List[Dict]] = None, mode: str = "both") -> str:
        for attempt in range(self.max_retries):
            try:
                response = self._send_ollama_request(user_input, history or [], mode)
                return self._parse_ollama_response(response)
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt == self.max_retries - 1:
                    return self._get_fallback_response()
                continue

    def _send_ollama_request(self, user_input: str, history: List[Dict], mode: str):
        messages = self._build_messages(user_input, history, mode)
        logger.debug(f"Sending to Ollama: {json.dumps(messages, indent=2)}")
        
        return requests.post(
            self.ollama_url,
            json={
                "model": self.model,
                "messages": messages,
                "stream": False,
                "options": {"temperature": 0.7}
            },
            timeout=self.timeout
        )

    def _parse_ollama_response(self, response):
        try:
            response.raise_for_status()
            data = response.json()
            
            if not isinstance(data, dict) or 'message' not in data:
                raise ValueError("Invalid response format from Ollama")
                
            return data['message']['content']
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {str(e)}")
            raise ValueError("Invalid JSON response from Ollama")
            
    def _build_messages(self, user_input: str, history: List[Dict], mode: str) -> List[Dict]:
        system_prompt = {
            "solution": "Provide 1-2 practical suggestions after brief empathy.",
            "support": "Offer emotional validation and ask open-ended questions.",
            "both": "Alternate between support and solution-oriented responses."
        }.get(mode, "Respond helpfully")
        
        return [
            {"role": "system", "content": system_prompt},
            *history[-4:],  # Last 4 messages for context
            {"role": "user", "content": user_input}
        ]

    def _get_fallback_response(self) -> str:
        return "I'm having technical difficulties. Please try again in a moment."

assistant = MentalHealthAssistant()

def generate_response(user_input: str, history: Optional[List[Dict]] = None, mode: str = "both") -> str:
    return assistant.generate_response(user_input, history, mode)