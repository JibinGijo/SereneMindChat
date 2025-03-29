from flask import Flask, render_template, request, jsonify, session
from datetime import datetime
import logging
import json

app = Flask(__name__)
app.secret_key = 'dev'  # Change for production
app.logger.setLevel(logging.DEBUG)

conversations = {}

@app.route('/')
def home():
    session['conversation_id'] = datetime.now().strftime("%Y%m%d%H%M%S")
    app.logger.debug("New session started")
    return render_template('chat.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message')
        mode = data.get('mode', 'both')
        conv_id = session.get('conversation_id')
        
        app.logger.debug(f"Received message: {user_message} | Mode: {mode}")

        if conv_id not in conversations:
            conversations[conv_id] = []
        
        conversations[conv_id].append({'role': 'user', 'content': user_message})
        
        try:
            from chatbot.ai_processor import generate_response
            bot_response = generate_response(user_message, conversations[conv_id], mode)
            app.logger.debug(f"Generated response: {bot_response}")
        except Exception as e:
            app.logger.error(f"AI Error: {str(e)}")
            bot_response = "I'm having trouble responding. Please try again."
        
        conversations[conv_id].append({'role': 'assistant', 'content': bot_response})
        
        return jsonify({
            'response': bot_response,
            'emergency': any(phrase in user_message.lower() 
                           for phrase in ["kill myself", "suicide", "end it all"])
        })

    except Exception as e:
        app.logger.error(f"Route error: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)