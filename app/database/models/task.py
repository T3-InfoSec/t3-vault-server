from sqlalchemy import (
    Column,
    Integer,
    LargeBinary,
    DateTime,
    BigInteger,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base


class Task(Base):
    __tablename__ = "tasks"

    db_key = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    client_id = Column(LargeBinary(16), ForeignKey("clients.client_id"), nullable=False)
    difficulty = Column(Integer, nullable=False)
    parameter_t = Column(BigInteger, nullable=False)
    # encrypt later
    parameter_product = Column(BigInteger, nullable=False)
    # encrypt later
    parameter_baseg = Column(BigInteger, nullable=False)
    fingerprint = Column(LargeBinary(16), nullable=False)
    first_assignment_id = Column(Integer, nullable=True)
    second_assignment_id = Column(Integer, nullable=True)
    num_assignments = Column(Integer, default=0)
    payment_id = Column(Integer, nullable=True)
    client = relationship("Client", back_populates="tasks")
