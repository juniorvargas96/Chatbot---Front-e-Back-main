import sqlite3
import hashlib
import json
from datetime import datetime, timedelta
from config.settings import settings
import numpy as np
from sentence_transformers import SentenceTransformer
import logging

logger = logging.getLogger(__name__)


class ChatCache:
    def __init__(self, db_path='chat_cache.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.execute("PRAGMA journal_mode = WAL")  # Melhora performance de escrita
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2') # Modelo leve para embedding
        self._create_table()
        
    def _create_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS cache (
            id TEXT PRIMARY KEY,
            question TEXT NOT NULL,
            response TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            usage_count INTEGER DEFAULT 1,
            embedding BLOB NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_created_at ON cache(created_at);
        """
        self.conn.executescript(query)
        self.conn.commit()
    
    def _generate_id(self, question):
        """Gera ID único baseado na pergunta"""
        return hashlib.sha256(question.encode('utf-8')).hexdigest()
    
    def _get_embedding(self, text):
        """Gera embedding para o texto"""
        return self.embedding_model.encode(text)
    
    def _serialize_embedding(self, embedding):
        """Serializa o embedding Numpy array para armazenamento no SQLite"""
        return json.dumps(embedding.tolist())
    
    def _deserialize_embedding(self, blob):
        """Desserializa o embedding do SQLite para Numpy array"""
        return np.array(json.loads(blob))
    
    def get_similar_response(self, question, threshold=0.85):
        """
        Busca respostas similares no cache com base no embedding da pergunta
        retorna a resposta mais similar se a simiaridade for maior que o threshold
        """
        question_embedding = self._get_embedding(question)

        try:
            cursor = self.conn.execute("SELECT id, question, response, embedding, usage_count FROM cache")
            best_match = None
            best_score = 0

            for row in cursor:
                cache_id, cached_question, response, embedding_blob, count = row
                cached_embedding = self._deserialize_embedding(embedding_blob)

                #calcula similaridade de cosseno
                similarity = np.dot(question_embedding, cached_embedding) / (np.linalg.norm(question_embedding) * np.linalg.norm(cached_embedding)
                )

                if similarity > best_score:
                    best_score = similarity
                    best_match = (cache_id, response, count, cached_question)

            if best_score >= threshold:
                cache_id, response, count, cached_question = best_match
                # atualiza contagem de uso
                self.conn.execute(
                    "UPDATE cache SET usage_count = ? where id = ?",
                    (count +1, cache_id)
                )
                self.conn.commit()
                logger.info(f"Resposta similar encontrada (score: {best_score: .2f}): '{cached_question[:30]}...' para '{question[:30]}...'")
                return json.loads(response)
            return None
        except sqlite3.Error as e:
            print(f"Erro ao buscar similaridade no cache: {str(e)}")
            return None

    def get_response(self, question):
        """Busca resposta em exata ou similar em cache"""
        # Primeiro tenta encontrar correspondência exata
        cache_id = self._generate_id(question)
        cursor = self.conn.execute(
            "SELECT response, usage_count FROM cache WHERE id = ?",
            (cache_id, )
        )
        
        if result := cursor.fetchone():
            response, count = result
            # Atualiza contagem de uso
            self.conn.execute(
                "UPDATE cache SET usage_count = ? WHERE id = ?",
                (count + 1, cache_id)
            )
            self.conn.commit()
            return json.loads(response)

            #se não encontrar correspondência exata, busca por similaridade
        return self.get_similar_response(question)
            
    
    def save_response(self, question, response):
        """Salva nova resposta no cache com seu embedding"""
        cache_id = self._generate_id(question)
        embedding = self._get_embedding(question)
        serialized_embedding = self._serialize_embedding(embedding)

        try:
            self.conn.execute(
                "INSERT OR REPLACE INTO cache (id, question, response, embedding) VALUES (?, ?, ?, ?)",
                (cache_id, question, json.dumps(response), serialized_embedding)
            )
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Erro ao salvar no cache: {str(e)}")
            return False
    
    def clean_old_cache(self):
        """Remove entradas antigas do cache"""
        try:
            expiration_date = datetime.now() - timedelta(days=settings.CACHE_EXPIRATION_DAYS)
            self.conn.execute(
                "DELETE FROM cache WHERE created_at < ?",
                (expiration_date.strftime('%Y-%m-%d %H:%M:%S'),)
            )
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Erro ao limpar cache: {str(e)}")
            return False
    
    def get_cache_stats(self):
        """Retorna estatísticas do cache"""
        try:
            cursor = self.conn.execute("SELECT COUNT(*) AS total, SUM(usage_count) AS total_uses FROM cache")
            stats = cursor.fetchone()
            return {
                "total_entries": stats[0],
                "total_uses": stats[1] if stats[1] else 0
            }
        except sqlite3.Error:
            return {"total_entries": 0, "total_uses": 0}
    
    def close(self):
        try:
            self.conn.close()
        except sqlite3.Error:
            pass

# Singleton para fácil acesso
cache_manager = ChatCache()