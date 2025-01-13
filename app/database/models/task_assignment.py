from sqlalchemy import (
    Column,
    Integer,
    LargeBinary,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    Float,
    BINARY,
)
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base


class TaskAssignment(Base):
    __tablename__ = "task_assignments"
    db_key = Column(Integer, primary_key=True)
    task_id = Column(LargeBinary(16), ForeignKey("tasks.fingerprint"), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    delivery_at = Column(DateTime, nullable=True)
    deadline = Column(DateTime, nullable=True)
    complaint_deadline = Column(DateTime, nullable=True)
    elapsed_time = Column(Float, default=0.0)
    delivered_in_time = Column(
        Boolean, nullable=True
    )  # True if delivered before deadline
    complaint_id = Column(Integer, nullable=True)
    response_power = Column(Integer, nullable=True)  # Solver's response
    complaint_at = Column(DateTime, nullable=True)  # Null if no complaint
    validity = Column(Boolean, nullable=True)  # True if response is valid
    solver_id = Column(Integer, ForeignKey("providers.db_key"), nullable=False)
    task_key = Column(Integer, ForeignKey("tasks.db_key"), nullable=False)
