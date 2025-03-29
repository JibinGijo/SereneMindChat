from supabase import create_client, Client
import os
from typing import List, Dict, Optional
from datetime import datetime
import logging
import time  

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from supabase import create_client, Client
import os
from typing import List, Dict, Optional
from datetime import datetime
import logging
import time
from dotenv import load_dotenv  # Add this import

# Load environment variables FIRST
load_dotenv()  # <-- This line is crucial

# Then configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SupabaseManager:
    def __init__(self):
        """Initialize Supabase client with retry logic"""
        # Verify env vars are loaded
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_KEY')
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("Supabase credentials not found in environment variables")
            
        self.client = self._initialize_client()
        
    def _initialize_client(self, retries: int = 3) -> Client:
        """Initialize Supabase client with retry logic"""
        for attempt in range(retries):
            try:
                return create_client(
                    self.supabase_url,  # Use the instance variables
                    self.supabase_key
                )
            except Exception as e:
                logger.error(f"Supabase connection attempt {attempt + 1} failed: {str(e)}")
                if attempt == retries - 1:
                    raise
                time.sleep(2 ** attempt)

    def create_user_session(self, user_id: str, session_id: str) -> Dict:
        """Create a new user session"""
        try:
            # Upsert user record
            self.client.table('users').upsert({
                'user_id': user_id,
                'last_active': datetime.now().isoformat()
            }).execute()

            # Create session
            response = self.client.table('sessions').insert({
                'session_id': session_id,
                'user_id': user_id
            }).execute()
            return response.data[0]
        except Exception as e:
            logger.error(f"Error creating session: {str(e)}")
            raise

    # Chat Operations
    def log_message(self, session_id: str, message: str, 
                   is_from_user: bool, is_emergency: bool = False) -> Dict:
        """Store chat message with automatic timestamp"""
        try:
            response = self.client.table('chat_messages').insert({
                'session_id': session_id,
                'message_text': message,
                'is_from_user': is_from_user,
                'is_emergency': is_emergency
            }).execute()
            return response.data[0]
        except Exception as e:
            logger.error(f"Error logging message: {str(e)}")
            raise

    # Emergency Operations
    def log_emergency_location(self, session_id: str, lat: float, lng: float,
                              accuracy: Optional[float] = None, 
                              address: Optional[str] = None) -> Dict:
        """Record emergency location with reverse geocoding"""
        try:
            response = self.client.table('emergency_locations').insert({
                'session_id': session_id,
                'latitude': lat,
                'longitude': lng,
                'accuracy': accuracy,
                'address': address
            }).execute()
            return response.data[0]
        except Exception as e:
            logger.error(f"Error logging location: {str(e)}")
            raise

    def create_emergency_dispatch(self, location_id: int, responder_id: int) -> Dict:
        """Initiate emergency response protocol"""
        try:
            response = self.client.table('dispatches').insert({
                'location_id': location_id,
                'responder_id': responder_id,
                'status': 'pending'
            }).execute()
            return response.data[0]
        except Exception as e:
            logger.error(f"Error creating dispatch: {str(e)}")
            raise

    # Admin Operations
    def get_active_responders(self) -> List[Dict]:
        """Retrieve available responders"""
        try:
            response = self.client.table('responders').select(
                "responder_id,name,phone,email,last_available_at"
            ).eq('is_active', True).order('last_available_at', desc=True).execute()
            return response.data
        except Exception as e:
            logger.error(f"Error fetching responders: {str(e)}")
            return []

    def get_recent_emergencies(self, hours: int = 24, limit: int = 10) -> List[Dict]:
        """Get emergencies from past X hours"""
        try:
            response = self.client.rpc('get_recent_emergencies', {
                'hours_limit': hours,
                'max_results': limit
            }).execute()
            return response.data
        except Exception as e:
            logger.error(f"Error fetching emergencies: {str(e)}")
            return []

    def update_dispatch_status(self, dispatch_id: int, status: str) -> bool:
        """Update dispatch status (pending/dispatched/arrived/completed)"""
        try:
            self.client.table('dispatches').update({
                'status': status,
                'status_updated_at': datetime.now().isoformat()
            }).eq('dispatch_id', dispatch_id).execute()
            return True
        except Exception as e:
            logger.error(f"Error updating dispatch: {str(e)}")
            return False

    # Analytics
    def get_conversation_history(self, session_id: str) -> List[Dict]:
        """Retrieve full conversation history"""
        try:
            response = self.client.table('chat_messages').select("*").eq(
                'session_id', session_id
            ).order('created_at').execute()
            return response.data
        except Exception as e:
            logger.error(f"Error fetching conversation: {str(e)}")
            return []

# Singleton instance
db_manager = SupabaseManager()