# gemini_api.py (ou onde você centraliza suas chamadas de API)
from google import genai
import logging
import os

logger = logging.getLogger(__name__)

# Configure a chave da API (garanta que a variável de ambiente GEMINI_API_KEY esteja definida)
try:
    client = genai.Client()
except Exception as e:
    logger.error(f"Falha ao inicializar o cliente Gemini: {e}")
    client = None

def get_gemini_embedding(text: str) -> list[float] | None:
    """
    Gera o vetor de embedding de um texto usando a API do Gemini.
    """
    if not client:
        return None
        
    try:
        # Modelo de embedding recomendado pelo Google
        model = "text-embedding-004"
        
        # Chama a API
        response = client.models.embed_content(
            model=model,
            content=text,
            task_type="RETRIEVAL_DOCUMENT" # Ou outro tipo que se ajuste ao seu uso
        )
        
        # A API retorna o vetor como uma lista de floats
        return response["embedding"]
        
    except Exception as e:
        logger.error(f"Erro ao gerar embedding com Gemini: {e}")
        return None

# Para fins de teste e similaridade, precisamos de uma função de produto escalar básica:
def calculate_dot_product(vec1: list[float], vec2: list[float]) -> float:
    """Calcula o produto escalar (Similaridade de Cosseno com vetores normalizados)."""
    if not vec1 or not vec2 or len(vec1) != len(vec2):
        return 0.0
    
    # O embedding do Gemini já é normalizado, então o produto escalar é a Similaridade de Cosseno
    return sum(x * y for x, y in zip(vec1, vec2))