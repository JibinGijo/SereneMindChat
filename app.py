from flask import Flask, render_template, request, jsonify, session
from datetime import datetime
import json

app = Flask(__name__)
app.secret_key = 'dev'  # For session only - replace with random string in production

# In-memory storage (replace with database in production)
conversations = {}

@app.route('/')
def home():
    session['conversation_id'] = datetime.now().strftime("%Y%m%d%H%M%S")
    return render_template('chat.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    conv_id = session.get('conversation_id')
    
    if not conv_id in conversations:
        conversations[conv_id] = []
    
    conversations[conv_id].append({'role': 'user', 'content': user_message})
    
    try:
        from chatbot.ai_processor import generate_response
        bot_response = generate_response(user_message, conversations[conv_id])
    except Exception as e:
        bot_response = f"I'm having trouble responding. Please try again later. ({str(e)})"
    
    conversations[conv_id].append({'role': 'assistant', 'content': bot_response})
    
    return jsonify({
        'response': bot_response,
        'history': conversations[conv_id]
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)