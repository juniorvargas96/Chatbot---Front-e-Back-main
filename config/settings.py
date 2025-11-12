import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

class Settings:

    # Configurações de API
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    if not GOOGLE_API_KEY:
        raise RuntimeError("Variável de ambiente GOOGLE_API_KEY não encontrada!")

    # URLs para scraping
    URLS_PARA_SCRAPING = [
    "https://www.jovemprogramador.com.br/sobre.php",
    "https://www.jovemprogramador.com.br/duvidas.php",
    "https://www.jovemprogramador.com.br/patrocinadores.php",
    "https://www.jovemprogramador.com.br/hackathon/",
    ]

    # Configurações de scraping
    TIMEOUT_REQUISICAO = 15
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"

    # Configurações de modelo
    MODEL_NAME = 'gemini-flash-latest'
    GENERATION_CONFIG = {
        "max_output_tokens": 1000,
        "temperature": 0.3
    }
    SAFETY_SETTINGS = {
        "HARASSMENT": "block_none",
        "HATE": "block_none",
        "SEXUAL": "block_none",
        "DANGEROUS": "block_none"
    }

    # Configurações de histórico
    MAX_HISTORY = 10

    # Configurações de cache
    CACHE_FILE = "content_cache.txt"
    USE_CACHE = False  # Mudar para True durante desenvolvimento

    # Configurações de validação
    TAMANHO_MAXIMO_PERGUNTA = 500

    # Adicione no final:
    CACHE_EXPIRATION_DAYS = 30  # Expira após 30 dias

    # Configurações de embeddings
    SIMILARITY_THRESHOLD = 0.85 #Limiar de similaridade para considerar perguntas equivalentes
    EMBEDDING_MODEL = 'all-MiniLM-L6-v2'

settings = Settings()