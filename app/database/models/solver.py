from sqlalchemy import BINARY, Column, Integer, LargeBinary, String, DateTime, Boolean, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base

class Solver(Base):
    __tablename__ = "solvers"
    
    db_key = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    solver_id = Column(LargeBinary(16), unique=True, nullable=False)  # fingerprint of cryptographic key
    connection_id = Column(String, nullable=True)  # current websocket connection id
    is_online = Column(Boolean, default=False)
    tasks_taken = Column(Integer, default=0)
    tasks_delivered = Column(Integer, default=0)
    tasks_expired = Column(Integer, default=0)
    tasks_not_complained = Column(Integer, default=0)
    tasks_complained = Column(Integer, default=0)
    complaints_won = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)
    computation_power_score = Column(Float, default=0.0)
    reputation_score = Column(Float, default=0.0)
    subscription_payment_id = Column(Integer, nullable=True)
