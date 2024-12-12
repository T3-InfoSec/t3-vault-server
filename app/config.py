from cryptography.fernet import Fernet
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()
# dot.env


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./data/t3v.sqlite"
    ENCRYPTION_KEY_PASSWORD: str
    class Config:
        env_file = ".env"

settings = Settings()
