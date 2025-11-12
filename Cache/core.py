# chatbot_jp/cache/core.py
import sqlite3
import hashlib
import json
from datetime import datetime, timedelta
from contextlib import contextmanager

class ChatCache:
    def __init__(self, db_path='chat_cache.db'):
        self.db_path = db_path
        self._initialize_db()
    
    @contextmanager
    def _get_cursor(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA journal_mode = WAL")
        try:
            yield conn.cursor()
            conn.commit()
        finally:
            conn.close()
    
    def _initialize_db(self):
        with self._get_cursor() as cursor:
            cursor.executescript("""
                CREATE TABLE IF NOT EXISTS cache (
                    id TEXT PRIMARY KEY,
                    question TEXT NOT NULL,
                    response TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    usage_count INTEGER DEFAULT 1,
                    last_accessed TIMESTAMP
                );
                CREATE INDEX IF NOT EXISTS idx_usage ON cache(usage_count);
                CREATE INDEX IF NOT EXISTS idx_accessed ON cache(last_accessed);
            """)
    
    def get_response(self, question):
        cache_id = self._generate_id(question)
        with self._get_cursor() as cursor:
            cursor.execute(
                """UPDATE cache SET 
                    usage_count = usage_count + 1,
                    last_accessed = CURRENT_TIMESTAMP
                WHERE id = ? RETURNING response""",
                (cache_id,)
            )
            if result := cursor.fetchone():
                return json.loads(result[0])
        return None

    # ... (outros métodos básicos)