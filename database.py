import sqlite3
import os

DB_NAME = 'chat_history.db'

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_message TEXT NOT NULL,
            bot_response TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def save_interaction(user_message, bot_response):
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO interactions (user_message, bot_response) VALUES (?, ?)',
        (user_message, bot_response)
    )
    conn.commit()
    conn.close()

def get_history():
    conn = get_db_connection()
    interactions = conn.execute('SELECT * FROM interactions ORDER BY timestamp ASC').fetchall()
    conn.close()
    return [{"user_message": row['user_message'], "bot_response": row['bot_response'], "timestamp": row['timestamp']} for row in interactions]
