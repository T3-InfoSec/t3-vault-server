# app/utils/encryption.py
from cryptography.fernet import Fernet
from ..config import settings
import hashlib

class Encryption:
    def __init__(self):
        self.fernet = Fernet(settings.ENCRYPTION_KEY.encode())
    
    def encrypt(self, data: str) -> bytes:
        return self.fernet.encrypt(data.encode())
    
    def decrypt(self, data: bytes) -> str:
        return self.fernet.decrypt(data).decode()

    @staticmethod
    def generate_fingerprint(input_string: str) -> bytes:
        """
        Generate a 16-byte fingerprint from input string.
        
        Args:
            input_string: The input string to generate fingerprint from
            
        Returns:
            bytes: A 16-byte fingerprint
        """
        # Generate SHA-256 hash and take first 16 bytes
        return hashlib.sha256(input_string.encode()).digest()[:16]

    @staticmethod
    def fingerprint_to_hex(fingerprint: bytes) -> str:
        """
        Convert binary fingerprint to hex string for display/logging
        
        Args:
            fingerprint: 16-byte fingerprint
            
        Returns:
            str: Hex string representation
        """
        return fingerprint.hex()

    @staticmethod
    def hex_to_fingerprint(hex_string: str) -> bytes:
        """
        Convert hex string back to binary fingerprint
        
        Args:
            hex_string: Hex string representation of fingerprint
            
        Returns:
            bytes: 16-byte fingerprint
        """
        return bytes.fromhex(hex_string)