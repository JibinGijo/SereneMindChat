import requests
import logging
from typing import Optional, List, Dict

logger = logging.getLogger(__name__)

class MentalHealthAssistant:
    def __init__(self):
        self.ollama_url = "http://localhost:11434/api/chat"
        self.model = "gemma:2b"  # or "llama2" for more conversational tone
        self.timeout = 30
        
    def generate_response(self, user_input: str, history: Optional[List[Dict]] = None) -> str:
        try:
            messages = [
                {
                    "role": "system", 
                    "content": "You are a compassionate listener. Respond naturally like a human friend would."
                },
                {"role": "user", "content": user_input}
            ]
            
            # Include conversation history if available
            if history:
                messages = history[-4:] + messages  # Keep last 4 messages for context
                
            response = requests.post(
                self.ollama_url,
                json={
                    "model": self.model,
                    "messages": messages,
                    "options": {
                        "temperature": 0.7,  # Balanced creativity
                        "num_ctx": 2048       # Better context understanding
                    }
                },
                timeout=self.timeout
            )
            response.raise_for_status()
            
            return response.json()['message']['content'].strip()
            
        except requests.exceptions.Timeout:
            return "I need a moment to think about that..."
        except Exception as e:
            logger.error(f"Response error: {str(e)}")
            return "I missed that. Could you say it again?"

assistant = MentalHealthAssistant()

def generate_response(user_input: str, history: Optional[List[Dict]] = None) -> str:
    return assistant.generate_response(user_input, history)