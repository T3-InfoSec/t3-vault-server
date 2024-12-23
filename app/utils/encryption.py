from ..config import settings
from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import base64
import hashlib
import os  # To generate a nonce

class Encryption:

    def __init__(self):
        password = settings.PLACEHOLDER_ENCRYPTION_KEY_PASSWORD.encode()
        self.key = hashlib.sha256(password).digest()

    def encrypt(self, plaintext):
        # Generate a random nonce
        nonce = os.urandom(12)  # GCM standard recommends a 12-byte nonce
        cipher = Cipher(algorithms.AES(self.key), modes.GCM(nonce), backend=default_backend())
        encryptor = cipher.encryptor()
        
        # Encrypt the plaintext
        ciphertext = encryptor.update(plaintext.encode()) + encryptor.finalize()
        
        # Combine nonce, ciphertext, and the tag, then encode to base64
        return base64.b64encode(nonce + ciphertext + encryptor.tag).decode()

    def decrypt(self, encrypted_text):
        raw = base64.b64decode(encrypted_text)
        nonce = raw[:12]  # First 12 bytes are the nonce
        tag = raw[-16:]   # Last 16 bytes are the tag
        ciphertext = raw[12:-16]  # The rest is the ciphertext
        
        cipher = Cipher(algorithms.AES(self.key), modes.GCM(nonce, tag), backend=default_backend())
        decryptor = cipher.decryptor()
        
        # Decrypt the ciphertext
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        return plaintext.decode()

    @staticmethod
    def generate_fingerprint(input_string: str) -> bytes:
        return hashlib.sha256(input_string.encode()).digest()[:16]

    @staticmethod
    def fingerprint_to_hex(fingerprint: bytes) -> str:
        return fingerprint.hex()

    @staticmethod
    def hex_to_fingerprint(hex_string: str) -> bytes:
        return bytes.fromhex(hex_string)
