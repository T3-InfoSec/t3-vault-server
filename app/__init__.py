# app/__init__.py
from .config import settings
from .main import app

__version__ = "0.1.0"

# app/database/__init__.py
from .database import Base, engine, SessionLocal, get_db
from .database.models import Client, Solver

__all__ = ['Base', 'engine', 'SessionLocal', 'get_db', 'Client', 'Solver']

# app/services/__init__.py
from .connection_manager import ConnectionManager

__all__ = ['ConnectionManager']

# app/utils/__init__.py
from .encryption import Encryption

__all__ = ['Encryption']