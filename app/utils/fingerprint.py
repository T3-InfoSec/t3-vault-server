import hashlib

class Fingerprint:
    @staticmethod
    def generate_fingerprint(input_string: str) -> bytes:
        return hashlib.sha256(input_string.encode()).digest()[:16]

    @staticmethod
    def fingerprint_to_hex(fingerprint: bytes) -> str:
        return fingerprint.hex()

    @staticmethod
    def hex_to_fingerprint(hex_string: str) -> bytes:
        return bytes.fromhex(hex_string)
