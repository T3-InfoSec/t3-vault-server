from sqlalchemy import (
    CheckConstraint,
    Column,
    ForeignKey,
    Integer,
    String,
    DateTime,
    Float,
)
from datetime import datetime
from ..database import Base
from sqlalchemy.orm import relationship


class Booking(Base):
    __tablename__ = "bookings"

    db_key = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.now)
    provider_id = Column(
        Integer, ForeignKey("providers.db_key"), nullable=True
    )  # Assigned provider's ID
    price = Column(Float, nullable=False)  # Price of the booking
    status = Column(String, nullable=False, default="pending")  # Status of the booking
    payment_id = Column(String, default="btcx123YF")
    # Relationships
    provider = relationship("Provider", back_populates="bookings")

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'completed', 'cancelled', 'expired')",
            name="valid_booking_status",
        ),
    )
