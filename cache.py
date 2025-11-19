import sqlite3
import hashlib
import json
from datetime import datetime, timedelta
from config.settings import settings
import logging

# IMPORTANTE: REMOVA as linhas de importação de numpy e SentenceTransformer!
# from sentence_transformers import SentenceTransformer
# import numpy as np

# Importa as novas funções do módulo que chama o Gemini (ou inclua-as aqui)
from gemini_api import get_gemini_embedding, calculate_dot_produc

logger = logging.getLogger(__name__)


class ChatCache:
    def __init__(self, db_path='chat_cache.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(
            db_path,
            check_same_thread=False,
            timeout=10
        )
        self.conn.execute("PRAGMA journal_mode = WAL")
        self.conn.execute("PRAGMA synchronous = NORMAL")
        
        # O modelo de embedding é agora o serviço do Gemini (não precisa carregar localmente)
        # self.embedding_model = None REMOVIDO
        
        self._create_table()

    # _load_model() e _create_table() são REMOVIDOS/DEIXADOS COMO ESTÃO

    def _create_table(self):
        # ... (Mantém a tabela como está)
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
        return text.strip().lower()

    def _generate_id(self, question):
        return hashlib.sha256(question.encode("utf-8")).hexdigest()

    def _get_embedding(self, text):
        """SUBSTITUIÇÃO: Gera embedding usando a API do Gemini."""
        return get_gemini_embedding(text) # Retorna list[float] ou None

    def _serialize_embedding(self, embedding):
        """Serializa a lista de floats."""
        return json.dumps(embedding)

    def _deserialize_embedding(self, blob):
        """Deserializa para lista de floats."""
        return json.loads(blob)
    
    def get_similar_response(self, question, threshold=0.80):
        question_norm = self._normalize_text(question)
        question_emb = self._get_embedding(question_norm) # Lista de floats

        if not question_emb:
            # Se a API falhou, não podemos buscar similaridade. Retorna None
            return None 

        try:
            cursor = self.conn.execute(
                "SELECT id, question, response, embedding, usage_count FROM cache"
            )

            best = None
            best_score = 0

            for cache_id, cached_q, resp, emb_blob, count in cursor:
                cached_emb = self._deserialize_embedding(emb_blob) 

                # Usa a função de produto escalar (sem numpy)
                similarity = calculate_dot_product(question_emb, cached_emb) 

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
    
    # ... (O resto dos métodos save_response, get_response, clean_old_cache e stats permanecem os mesmos,
    # usando _get_embedding e as funções de (des)serialização sem numpy). ...