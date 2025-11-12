# chatbot_jp/cache/analytics.py
import sqlite3
from collections import defaultdict

class CacheAnalytics:
    def __init__(self, db_path):
        self.db_path = db_path
    
    def get_usage_stats(self, days=30):
        with sqlite3.connect(self.db_path) as conn:
            return {
                'total_hits': self._get_total_hits(conn),
                'popular_questions': self._get_popular_questions(conn, 5),
                'hit_rate': self._calculate_hit_rate(conn, days)
            }
    
    def _get_total_hits(self, conn):
        return conn.execute("SELECT SUM(usage_count) FROM cache").fetchone()[0] or 0
    
    def _get_popular_questions(self, conn, limit):
        return dict(conn.execute(
            "SELECT question, usage_count FROM cache ORDER BY usage_count DESC LIMIT ?",
            (limit,)
        ).fetchall())