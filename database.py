import sqlite3
import os

DB_NAME = 'chat_history.db'

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    # Users table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    
    # Interactions table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            user_message TEXT NOT NULL,
            bot_response TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Safely migrate existing interactions table to add user_id if needed
    try:
        conn.execute('ALTER TABLE interactions ADD COLUMN user_id INTEGER REFERENCES users(id)')
    except sqlite3.OperationalError:
        pass # Column already exists
        
    conn.commit()
    conn.close()

def save_interaction(user_id, user_message, bot_response):
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO interactions (user_id, user_message, bot_response) VALUES (?, ?, ?)',
        (user_id, user_message, bot_response)
    )
    conn.commit()
    conn.close()

def get_history(user_id):
    conn = get_db_connection()
    interactions = conn.execute('SELECT * FROM interactions WHERE user_id = ? ORDER BY timestamp ASC', (user_id,)).fetchall()
    conn.close()
    return [{"user_message": row['user_message'], "bot_response": row['bot_response'], "timestamp": row['timestamp']} for row in interactions]

def create_user(username, password_hash):
    conn = get_db_connection()
    try:
        conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password_hash))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_user_by_username(username):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    return dict(user) if user else None
