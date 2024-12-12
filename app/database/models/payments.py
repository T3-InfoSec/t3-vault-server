from sqlalchemy import CHAR, DECIMAL, Column, Integer, String, DateTime, Boolean, ForeignKey
from datetime import datetime
from ..database import Base
from sqlalchemy.orm import relationship

class Payment(Base):
    __tablename__ = "payments"

    db_key = Column(Integer, primary_key=True)  # Unique identifier for each payment
    created_at = Column(DateTime, default=datetime.utcnow)  # Date and time the payment was created
    currency_id = Column(Integer, ForeignKey("currencies.db_key"), nullable=False)  # Foreign key to Currency Index
    method_id = Column(Integer, ForeignKey("payment_methods.db_key"), nullable=False)  # Foreign key to Method Index
    reason_id = Column(Integer, ForeignKey("payment_reasons.db_key"), nullable=False)  # Foreign key to Reason Index
    amount = Column(DECIMAL(20,8), nullable=False)  # Amount in smallest currency unit (e.g., cents)
    # Relationships
    currency = relationship("Currency", back_populates="payments")
    method = relationship("PaymentMethod", back_populates="payments")
    reason = relationship("PaymentReason", back_populates="payments")


class Currency(Base):
    __tablename__ = "currencies"
    db_key = Column(Integer, primary_key=True)  # Unique identifier for each currency
    name = Column(CHAR(3), nullable=False)  # Name of the currency (e.g., USD, BTC, SAT)
    currently_accepted = Column(Boolean, default=True)  # Whether the currency is currently accepted
    # Relationship
    payments = relationship("Payment", back_populates="currency")


class PaymentMethod(Base):
    __tablename__ = "payment_methods"
    db_key = Column(Integer, primary_key=True)  # Unique identifier for each payment method
    name = Column(String, nullable=False)  # Name of the payment method (e.g. Monero, PayPal, Lightning,)
    currently_accepted = Column(Boolean, default=True)  # Whether the payment method is currently accepted
    # Relationship
    payments = relationship("Payment", back_populates="method")


class PaymentReason(Base):
    __tablename__ = "payment_reasons"
    db_key = Column(Integer, primary_key=True)  # Unique identifier for each payment reason
    description = Column(String, nullable=False)  # Description of the reason (e.g., "Subscription", "Donation")    
    # Relationship
    payments = relationship("Payment", back_populates="reason")
