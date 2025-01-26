from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from ..config import settings




engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()    
    from app.utils.boostrap_db_datas import bootstrap_data # Lazy import
    bootstrap_data(session=db)
    try:
        yield db
    finally:
        db.close()



