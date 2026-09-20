import sqlite3, json, os
from datetime import datetime, timezone

DB_PATH = os.getenv("DB_PATH", "sales_assistant.db")

def conn():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c

def init_db():
    c=conn()
    c.executescript('''
    CREATE TABLE IF NOT EXISTS conversations (
      id TEXT PRIMARY KEY, channel TEXT NOT NULL, sender_id TEXT NOT NULL,
      sender_name TEXT, status TEXT DEFAULT 'new', assigned_rep TEXT,
      qualification_json TEXT, takeover INTEGER DEFAULT 0, created_at TEXT, updated_at TEXT
    );
    CREATE TABLE IF NOT EXISTS messages (
      id INTEGER PRIMARY KEY AUTOINCREMENT, conversation_id TEXT, direction TEXT,
      body TEXT, provider_message_id TEXT, created_at TEXT
    );
    CREATE TABLE IF NOT EXISTS actions (
      id INTEGER PRIMARY KEY AUTOINCREMENT, conversation_id TEXT, action TEXT,
      detail TEXT, created_at TEXT
    );
    CREATE TABLE IF NOT EXISTS bookings (
      id INTEGER PRIMARY KEY AUTOINCREMENT, conversation_id TEXT, slot_start TEXT,
      slot_end TEXT, calendar_event_id TEXT UNIQUE, idempotency_key TEXT UNIQUE,
      created_at TEXT
    );
    ''')
    c.commit(); c.close()

def now(): return datetime.now(timezone.utc).isoformat()

def log_action(cid, action, detail):
    c=conn(); c.execute("INSERT INTO actions(conversation_id,action,detail,created_at) VALUES(?,?,?,?)",(cid,action,detail,now())); c.commit(); c.close()
