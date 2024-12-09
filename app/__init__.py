# app/__init__.py
from .config import settings
from .main import app
from app.database.events import task_event



__version__ = "0.1.0"

# app/database/__init__.py
from .database.database import Base, engine, SessionLocal, get_db
from .database.models.solver import Solver
from .database.models.client import Client
from .database.models.task import Task

__all__ = [
    "Base",
    "engine",
    "SessionLocal",
    "get_db",
    "Client",
    "Solver",
    "Task",
]

# app/services/__init__.py
from .services.connection_manager import ConnectionManager

__all__ = ["ConnectionManager"]

# app/utils/__init__.py
from .utils.encryption import Encryption

__all__ = ["Encryption"]
