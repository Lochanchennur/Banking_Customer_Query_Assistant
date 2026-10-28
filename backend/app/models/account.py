from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.session import Base

class Account(Base):
    __tablename__ = "accounts"

    id = Column(String, primary_key=True, index=True)
    customer_id = Column(String, ForeignKey("customers.id"), nullable=False, index=True)
    account_number_masked = Column(String, nullable=False)
    account_type = Column(String, nullable=False)  # CHECKING, SAVINGS, INVESTMENT, CREDIT
    account_name = Column(String, nullable=False)
    currency = Column(String, default="INR")
    balance = Column(Float, default=0.0)
    available_balance = Column(Float, default=0.0)
    status = Column(String, default="ACTIVE")  # ACTIVE, DORMANT, BLOCKED
    interest_rate = Column(Float, default=0.0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    customer = relationship("Customer", back_populates="accounts")
    transactions = relationship("Transaction", back_populates="account", cascade="all, delete-orphan")
