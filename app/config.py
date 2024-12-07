from cryptography.fernet import Fernet
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./data/t3v.sqlite"
    ENCRYPTION_KEY: str = "5XKbXMqRAuGiN5nt2ZRKmRlYN1XpdpB_FROVDXG1QK8="

settings = Settings()
