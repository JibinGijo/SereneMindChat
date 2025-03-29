import mysql.connector
from mysql.connector import Error
from typing import Optional, Dict, List
import os
from datetime import datetime

class DatabaseManager:
    def __init__(self):
        self.connection = None
        self.connect()
        
    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                database=os.getenv('DB_NAME', 'mental_health_chat'),
                user=os.getenv('DB_USER', 'chatbot_admin'),
                password=os.getenv('DB_PASSWORD', 'secure_password'),
                port=os.getenv('DB_PORT', 3306)
            )
            print("Database connection established")
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            raise

    def log_message(self, session_id: str, message: str, is_from_user: bool, is_emergency: bool = False) -> int:
        query = """
        INSERT INTO chat_messages (session_id, message_text, is_from_user, is_emergency)
        VALUES (%s, %s, %s, %s)
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, (session_id, message, is_from_user, is_emergency))
            self.connection.commit()
            return cursor.lastrowid
        except Error as e:
            print(f"Error logging message: {e}")
            return -1

    def log_location(self, session_id: str, lat: float, lng: float, accuracy: Optional[float] = None, address: Optional[str] = None) -> int:
        query = """
        INSERT INTO emergency_locations (session_id, latitude, longitude, accuracy, address)
        VALUES (%s, %s, %s, %s, %s)
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, (session_id, lat, lng, accuracy, address))
            self.connection.commit()
            return cursor.lastrowid
        except Error as e:
            print(f"Error logging location: {e}")
            return -1

    def create_dispatch(self, location_id: int, responder_id: int) -> int:
        query = """
        INSERT INTO dispatches (location_id, responder_id)
        VALUES (%s, %s)
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, (location_id, responder_id))
            self.connection.commit()
            return cursor.lastrowid
        except Error as e:
            print(f"Error creating dispatch: {e}")
            return -1

    def get_active_responders(self) -> List[Dict]:
        query = """
        SELECT responder_id, name, phone FROM responders 
        WHERE is_active = TRUE 
        ORDER BY last_available DESC
        LIMIT 5
        """
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query)
            return cursor.fetchall()
        except Error as e:
            print(f"Error fetching responders: {e}")
            return []

    def close(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Database connection closed")

# Singleton instance
db_manager = DatabaseManager()