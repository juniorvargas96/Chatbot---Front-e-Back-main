# chatbot_jp/config/cache_config.py
import os
from dotenv import load_dotenv

load_dotenv()

class CacheConfig:
    DB_PATH = os.getenv('CACHE_DB_PATH', 'chat_cache.db')
    ENCRYPTION_KEY = os.getenv('CACHE_ENCRYPTION_KEY')  # Gerar com Fernet.generate_key()
    MAX_SIZE_MB = int(os.getenv('CACHE_MAX_SIZE_MB', 100))
    CLEANUP_DAYS = int(os.getenv('CACHE_CLEANUP_DAYS', 30))