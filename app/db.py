# app/db.py
import sqlite3
from datetime import datetime

DB_PATH = "data/logs.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS inference_logs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  endpoint TEXT, 
                  timestamp TEXT, 
                  input_data TEXT)''') 
    conn.commit()
    conn.close()

def log_inference(endpoint: str, input_data: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO inference_logs (endpoint, timestamp, input_data) VALUES (?, ?, ?)",
              (endpoint, datetime.now().isoformat(), input_data))
    conn.commit()
    conn.close()