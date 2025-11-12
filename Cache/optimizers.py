# chatbot_jp/cache/optimizers.py
import sqlite3

class CacheOptimizer:
    def __init__(self, db_path):
        self.db_path = db_path
    
    def optimize_space(self, max_size_mb=100):
        """Mantém o cache abaixo do tamanho especificado"""
        current_size = self._get_db_size()
        while current_size > max_size_mb:
            self._remove_old_entries(10)
            current_size = self._get_db_size()
    
    def _get_db_size(self):
        with sqlite3.connect(self.db_path) as conn:
            return conn.execute(
                "SELECT page_count * page_size FROM pragma_page_count(), pragma_page_size()"
            ).fetchone()[0] / (1024 * 1024)  # Convert to MB
    
    def _remove_old_entries(self, batch_size):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """DELETE FROM cache WHERE id IN (
                    SELECT id FROM cache 
                    ORDER BY last_accessed ASC, usage_count ASC
                    LIMIT ?
                )""", (batch_size,)
            )
            conn.commit()