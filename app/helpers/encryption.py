from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64


AES_BLOCK_SIZE = 16  # Block size for AES (16 bytes)

def aes_encrypt(data: str, key: str) -> str:
    """
    Encrypts the given data using AES encryption.
    
    Args:
        data (str): The plaintext data to encrypt.
        key (str): The encryption key (must be 16, 24, or 32 bytes).
        
    Returns:
        str: The base64-encoded ciphertext.
    """
    cipher = AES.new(key.encode(), AES.MODE_CBC)
    iv = cipher.iv
    ciphertext = cipher.encrypt(pad(data.encode(), AES_BLOCK_SIZE))
    return base64.b64encode(iv + ciphertext).decode()

def aes_decrypt(ciphertext: str, key: str) -> str:
    """
    Decrypts the given AES-encrypted ciphertext.
    
    Args:
        ciphertext (str): The base64-encoded ciphertext to decrypt.
        key (str): The decryption key (must match the encryption key).
        
    Returns:
        str: The decrypted plaintext data.
    """
    raw = base64.b64decode(ciphertext)
    iv = raw[:AES_BLOCK_SIZE]
    cipher = AES.new(key.encode(), AES.MODE_CBC, iv)
    plaintext = unpad(cipher.decrypt(raw[AES_BLOCK_SIZE:]), AES_BLOCK_SIZE)
    return plaintext.decode()
