from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./taskdb.sqlite"
    ENCRYPTION_KEY: str = "your-encryption-key"
    
settings = Settings()