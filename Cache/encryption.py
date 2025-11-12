# chatbot_jp/cache/encryption.py
from cryptography.fernet import Fernet
import base64
import hashlib

class CacheEncryptor:
    def __init__(self, encryption_key=None):
        self.key = self._process_key(encryption_key)
        self.cipher = Fernet(self.key) if self.key else None
    
    def _process_key(self, key):
        if not key:
            return None
        return base64.urlsafe_b64encode(
            hashlib.sha256(key.encode()).digest()
        )

    def encrypt(self, text):
        return self.cipher.encrypt(text.encode()).decode() if self.cipher else text
    
    def decrypt(self, text):
        return self.cipher.decrypt(text.encode()).decode() if self.cipher else text