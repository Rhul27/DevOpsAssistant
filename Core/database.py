import sqlite3
from datetime import datetime

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect('devops_assistant.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS command_history
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  question TEXT, 
                  response TEXT, 
                  timestamp DATETIME)''')
    conn.commit()
    conn.close()

init_db()

def save_command_history(question, response):
    conn = sqlite3.connect('devops_assistant.db')
    c = conn.cursor()
    c.execute("INSERT INTO command_history (question, response, timestamp) VALUES (?, ?, ?)",
              (question, response, datetime.now()))
    conn.commit()
    conn.close()

def get_cached_response(question):
    conn = sqlite3.connect('devops_assistant.db')
    c = conn.cursor()
    c.execute("SELECT response FROM command_history WHERE question = ? ORDER BY timestamp DESC LIMIT 1", (question,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

def get_command_history():
    conn = sqlite3.connect('devops_assistant.db')
    c = conn.cursor()
    c.execute("SELECT * FROM command_history ORDER BY timestamp DESC")
    history = c.fetchall()
    conn.close()
    return history