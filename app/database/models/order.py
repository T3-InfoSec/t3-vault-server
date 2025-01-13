from sqlalchemy import (
    CheckConstraint,
    Column,
    ForeignKey,
    Integer,
    String,
    DateTime,    
)
from datetime import datetime
from ..database import Base
from sqlalchemy.orm import relationship


class Order(Base):
    __tablename__ = 'orders'

    db_key = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.now)
    booking_id = Column(Integer, ForeignKey('bookings.id'), nullable=False)
    client_id = Column(Integer, ForeignKey('clients.id'), nullable=False)
    started_at = Column(DateTime, nullable=True)  # Start time for the order
    status = Column(String, nullable=False, default='in-progress')
    complaint_at = Column(DateTime, nullable=True)
    # Relationships
    booking = relationship('Booking', back_populates='orders')
    client = relationship('Client', back_populates='orders')    
    __table_args__ = (
        CheckConstraint("status IN ('in-progress', 'completed', 'cancelled', 'failed')", name='valid_order_status'),
    )