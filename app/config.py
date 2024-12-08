from cryptography.fernet import Fernet
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./data/t3v.sqlite"
    ENCRYPTION_KEY_PASSWORD: str = "vh9qFH0T9hzlhF++Z8aQjuMi++JCS2cPXZRnlL3/Jk4="


settings = Settings()
