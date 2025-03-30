import requests

class MentalHealthAssistant:
    def __init__(self):
        self.ollama_url = "http://localhost:11434/api/chat"
        self.model = "gemma:2b"  # Using Gemma 2B
        self.system_prompt = """You are a compassionate mental health assistant. 
        Respond with short, empathetic messages (1-2 sentences). Never give medical advice.
        If user expresses self-harm intent, gently ask if they want help connecting to professionals."""

    def generate_response(self, user_input, history=None):
        messages = [
            {"role": "system", "content": self.system_prompt},
            *(history or []),
            {"role": "user", "content": user_input}
        ]
        
        try:
            response = requests.post(
                self.ollama_url,
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": False,
                    "options": {"temperature": 0.7}
                },
                timeout=15  # Gemma may need slightly more time
            )
            response.raise_for_status()
            return response.json()['message']['content']
        
        except Exception as e:
            return self._emergency_fallback(user_input)

    def _emergency_fallback(self, user_input):
        lower_input = user_input.lower()
        if any(phrase in lower_input for phrase in ["kill myself", "end it all", "suicide"]):
            return "I'm very concerned. Please call 988 or text HOME to 741741. You're not alone."
        return "I'm having trouble responding. Would you like to try rephrasing?"

assistant = MentalHealthAssistant()

def generate_response(user_input, history=None):
    return assistant.generate_response(user_input, history)