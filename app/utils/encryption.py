from cryptography.fernet import Fernet
from ..config import settings

class Encryption:
    def __init__(self):
        self.fernet = Fernet(settings.ENCRYPTION_KEY.encode())
    
    def encrypt(self, data: str) -> bytes:
        return self.fernet.encrypt(data.encode())
    
    def decrypt(self, data: bytes) -> str:
        return self.fernet.decrypt(data).decode()
