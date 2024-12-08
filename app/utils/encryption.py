from ..config import settings
from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import base64
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64
import hashlib

class Encryption:

    def __init__(self):
        password = settings.ENCRYPTION_KEY_PASSWORD.encode()
        self.key = hashlib.sha256(password).digest()

    def encrypt(self, plaintext):
        cipher = AES.new(self.key, AES.MODE_CBC)
        iv = cipher.iv
        ciphertext = cipher.encrypt(pad(plaintext.encode(), AES.block_size))
        # Combine IV and ciphertext, encode to base64
        return base64.b64encode(iv + ciphertext).decode()

    def decrypt(self, encrypted_text):
        raw = base64.b64decode(encrypted_text)
        iv = raw[:AES.block_size]
        ciphertext = raw[AES.block_size:]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return unpad(cipher.decrypt(ciphertext), AES.block_size).decode()

    @staticmethod
    def generate_fingerprint(input_string: str) -> bytes:
        return hashlib.sha256(input_string.encode()).digest()[:16]

    @staticmethod
    def fingerprint_to_hex(fingerprint: bytes) -> str:
        return fingerprint.hex()

    @staticmethod
    def hex_to_fingerprint(hex_string: str) -> bytes:
        return bytes.fromhex(hex_string)