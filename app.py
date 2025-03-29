from flask import Flask, render_template, request, jsonify, session
from datetime import datetime
import secrets
import logging
import os``
from chatbot.ai_processor import generate_response

# Auto-generated secure secrets
SECRET_KEY = secrets.token_hex(32)  # Random 64-character hex string

app = Flask(__name__)
app.secret_key = SECRET_KEY

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/')
def home():
    """Initialize new chat session with random ID"""
    session['conversation_id'] = f"chat-{datetime.now().strftime('%Y%m%d%H%M%S')}-{secrets.token_hex(4)}"
    return render_template('chat.html')

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages with built-in error protection"""
    try:
        user_message = request.json.get('message', '').strip()
        if not user_message:
            return jsonify({'error': 'Empty message'}), 400
        
        # Get AI response with automatic retry
        response = generate_response(user_message)
        
        # Ensure valid response
        if not response or response.lower() in ('undefined', 'null', 'none'):
            response = "I'm not sure how to respond to that. Could you tell me more?"
        
        return jsonify({
            'response': response,
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        return jsonify({
            'response': "Let me think about that and try again...",
            'error': 'Internal error'
        }), 500

if __name__ == '__main__':
    # Generate self-signed cert for HTTPS if needed
    app.run(
        host='0.0.0.0',
        port=5000,
        ssl_context='adhoc' if os.getenv('USE_HTTPS') else None,
        debug=False
    )