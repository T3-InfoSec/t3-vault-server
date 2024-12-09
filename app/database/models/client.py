from sqlalchemy import BINARY, Column, Integer, LargeBinary, String, DateTime, Boolean, Float
from datetime import datetime
from ..database import Base
from sqlalchemy.orm import relationship

class Client(Base):
    __tablename__ = "clients"
    
    db_key = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    client_id = Column(LargeBinary(16), unique=True, nullable=False)  # fingerprint of cryptographic key
    connection_id = Column(String, nullable=True)  # current websocket connection id
    is_connected = Column(Boolean, default=False)
    tasks_requested = Column(Integer, default=0)
    tasks_received = Column(Integer, default=0)
    tasks_complained = Column(Integer, default=0)
    tasks_accepted = Column(Integer, default=0)
    acceptance_rate = Column(Float, default=0.0)
    reputation = Column(Float, default=0.0)
    subscription_payment_id = Column(Integer, nullable=True)
    tasks = relationship("Task", back_populates="client")
