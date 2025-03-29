from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from datetime import datetime
import logging
from database import db_manager
from chatbot.emergency import check_emergency
from chatbot.ai_processor import generate_response
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET', 'dev-secret-key')
app.config['SESSION_TYPE'] = 'filesystem'

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Store conversations in memory (fallback)
conversations = {}

# Admin authentication decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def home():
    session['conversation_id'] = f"conv-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    return render_template('chat.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message')
    mode = data.get('mode', 'both')
    conv_id = session.get('conversation_id')
    
    try:
        # Check for emergency keywords
        emergency_status = check_emergency(user_message)
        if emergency_status['is_emergency']:
            db_manager.log_message(conv_id, user_message, True, True)
            return jsonify({
                'response': emergency_status['message'],
                'emergency': True
            })
        
        # Normal response
        response = generate_response(user_message, None, mode)
        db_manager.log_message(conv_id, user_message, True)
        db_manager.log_message(conv_id, response, False)
        
        return jsonify({
            'response': response,
            'emergency': False
        })
        
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        return jsonify({
            'response': "I'm having trouble responding. Please try again.",
            'error': str(e)
        }), 500

@app.route('/emergency', methods=['POST'])
def handle_emergency():
    try:
        data = request.json
        conv_id = session.get('conversation_id')
        location = data.get('location')
        
        # Log emergency location
        loc_id = db_manager.log_location(
            session_id=conv_id,
            lat=location.get('lat'),
            lng=location.get('lng'),
            accuracy=location.get('accuracy'),
            address=location.get('address')
        )
        
        # Dispatch responder
        responders = db_manager.get_active_responders()
        if responders:
            db_manager.create_dispatch(loc_id, responders[0]['responder_id'])
        
        return jsonify({
            'status': 'help_dispatched',
            'responder': responders[0]['name'] if responders else None,
            'contact': responders[0]['phone'] if responders else '911'
        })
        
    except Exception as e:
        logger.error(f"Emergency error: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Admin routes
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if (request.form['username'] == os.getenv('ADMIN_USER', 'admin') and
            request.form['password'] == os.getenv('ADMIN_PASS', 'securepassword')):
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        return render_template('admin_login.html', error="Invalid credentials")
    return render_template('admin_login.html')

@app.route('/admin')
@admin_required
def admin_dashboard():
    try:
        # Get recent emergencies
        cursor = db_manager.connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT el.*, COUNT(cm.message_id) as msg_count 
            FROM emergency_locations el
            LEFT JOIN chat_messages cm ON el.session_id = cm.session_id
            GROUP BY el.location_id
            ORDER BY el.timestamp DESC
            LIMIT 10
        """)
        emergencies = cursor.fetchall()
        
        # Get responder status
        cursor.execute("""
            SELECT r.name, r.phone, r.email,
                   COUNT(d.dispatch_id) as total_dispatches,
                   SUM(CASE WHEN d.status = 'completed' THEN 1 ELSE 0 END) as completed
            FROM responders r
            LEFT JOIN dispatches d ON r.responder_id = d.responder_id
            GROUP BY r.responder_id
        """)
        responders = cursor.fetchall()
        
        return render_template('admin_dashboard.html',
                             emergencies=emergencies,
                             responders=responders)
        
    except Exception as e:
        logger.error(f"Admin dashboard error: {str(e)}")
        return render_template('admin_error.html', error=str(e))

@app.route('/admin/dispatch/<int:location_id>', methods=['POST'])
@admin_required
def dispatch_responder(location_id):
    try:
        responder_id = request.form.get('responder_id')
        if not responder_id:
            return jsonify({'error': 'Responder ID required'}), 400
            
        db_manager.create_dispatch(location_id, responder_id)
        return jsonify({'status': 'dispatched'})
        
    except Exception as e:
        logger.error(f"Dispatch error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))

@app.teardown_appcontext
def close_db_connection(exception=None):
    db_manager.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)