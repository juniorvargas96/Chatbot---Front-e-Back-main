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

        # Conexão otimizada para multithread
        self.conn = sqlite3.connect(
            db_path,
            check_same_thread=False,
            timeout=10
        )
        self.conn.execute("PRAGMA journal_mode = WAL")
        self.conn.execute("PRAGMA synchronous = NORMAL")

        self.embedding_model = None  # lazy-load

        self._create_table()

    def _load_model(self):
        """Carrega modelo apenas quando necessário."""
        if self.embedding_model is None:
            self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

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

    def _normalize_text(self, text):
        """Evita duplicações inúteis por caixa alta/baixa/espaços."""
        return text.strip().lower()

    def _generate_id(self, question):
        return hashlib.sha256(question.encode("utf-8")).hexdigest()

    def _get_embedding(self, text):
        """Gera e normaliza embedding."""
        self._load_model()
        vector = self.embedding_model.encode(text)
        return vector / (np.linalg.norm(vector) + 1e-10)

    def _serialize_embedding(self, embedding):
        return json.dumps(embedding.tolist())

    def _deserialize_embedding(self, blob):
        arr = np.array(json.loads(blob))
        return arr / (np.linalg.norm(arr) + 1e-10)

    def get_similar_response(self, question, threshold=0.80):
        """Busca pergunta mais similar via embeddings."""
        question_norm = self._normalize_text(question)
        question_emb = self._get_embedding(question_norm)

        try:
            cursor = self.conn.execute(
                "SELECT id, question, response, embedding, usage_count FROM cache"
            )

            best = None
            best_score = 0

            for cache_id, cached_q, resp, emb_blob, count in cursor:
                cached_emb = self._deserialize_embedding(emb_blob)

                similarity = float(np.dot(question_emb, cached_emb))

                if similarity > best_score:
                    best_score = similarity
                    best = (cache_id, resp, count, cached_q)

            if best and best_score >= threshold:
                cache_id, response, usage, cached_q = best
                self.conn.execute(
                    "UPDATE cache SET usage_count = ? WHERE id = ?",
                    (usage + 1, cache_id)
                )
                self.conn.commit()

                logger.info(
                    f"[CACHE HIT - Similaridade {best_score:.2f}] "
                    f"'{cached_q[:40]}...' ↔ '{question[:40]}...'"
                )

                return json.loads(response)

            return None

        except Exception as e:
            logger.error(f"Erro ao buscar similaridade no cache: {e}")
            return None

    def get_response(self, question):
        question_norm = self._normalize_text(question)
        cache_id = self._generate_id(question_norm)

        cursor = self.conn.execute(
            "SELECT response, usage_count FROM cache WHERE id = ?",
            (cache_id,)
        )

        if result := cursor.fetchone():
            response, usage = result

            self.conn.execute(
                "UPDATE cache SET usage_count = ? WHERE id = ?",
                (usage + 1, cache_id)
            )
            self.conn.commit()

            logger.info(f"[CACHE HIT - Exata] '{question[:40]}...'")

            return json.loads(response)

        return self.get_similar_response(question_norm)

    def save_response(self, question, response):
        """Salva no cache sem resetar usage_count de itens já existentes."""
        question_norm = self._normalize_text(question)
        cache_id = self._generate_id(question_norm)

        embedding = self._get_embedding(question_norm)
        serialized = self._serialize_embedding(embedding)

        try:
            cursor = self.conn.execute(
                "SELECT id FROM cache WHERE id = ?", (cache_id,)
            )

            if cursor.fetchone():
                # Atualiza apenas conteúdo da resposta
                self.conn.execute(
                    "UPDATE cache SET question = ?, response = ?, embedding = ? WHERE id = ?",
                    (question_norm, json.dumps(response), serialized, cache_id)
                )
            else:
                # Insere novo item
                self.conn.execute(
                    "INSERT INTO cache (id, question, response, embedding) VALUES (?, ?, ?, ?)",
                    (cache_id, question_norm, json.dumps(response), serialized)
                )

            self.conn.commit()
            return True

        except Exception as e:
            logger.error(f"Erro ao salvar cache: {e}")
            return False

    def clean_old_cache(self):
        """Remove entradas antigas."""
        try:
            expiration = datetime.now() - timedelta(days=settings.CACHE_EXPIRATION_DAYS)
            self.conn.execute(
                "DELETE FROM cache WHERE created_at < ?",
                (expiration.strftime("%Y-%m-%d %H:%M:%S"),)
            )
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Erro ao limpar cache: {e}")
            return False

    def get_cache_stats(self):
        cursor = self.conn.execute(
            "SELECT COUNT(*), SUM(usage_count) FROM cache"
        )
        total, uses = cursor.fetchone()

        return {
            "total_entries": total or 0,
            "total_uses": uses or 0
        }

    def close(self):
        try:
            self.conn.close()
        except:
            pass


# Singleton
cache_manager = ChatCache()
