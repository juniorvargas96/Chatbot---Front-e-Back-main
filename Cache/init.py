# chatbot_jp/cache/__init__.py
from .core import ChatCache
from .encryption import CacheEncryptor
from .analytics import CacheAnalytics
from .optimizers import CacheOptimizer
from config.cache_config import CacheConfig

class EnhancedChatCache(ChatCache):
    def __init__(self):
        config = CacheConfig()
        super().__init__(config.DB_PATH)
        self.encryptor = CacheEncryptor(config.ENCRYPTION_KEY)
        self.optimizer = CacheOptimizer(config.DB_PATH)
        self.analytics = CacheAnalytics(config.DB_PATH)
    
    def get_response(self, question):
        response = super().get_response(question)
        return self.encryptor.decrypt(response) if response else None
    
    def save_response(self, question, response):
        encrypted = self.encryptor.encrypt(response)
        super().save_response(question, encrypted)
        self.optimizer.optimize_space()

# Singleton
cache_manager = EnhancedChatCache()
