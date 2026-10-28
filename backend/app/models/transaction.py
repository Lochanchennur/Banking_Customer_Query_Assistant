from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.session import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String, primary_key=True, index=True)
    account_id = Column(String, ForeignKey("accounts.id"), nullable=False, index=True)
    customer_id = Column(String, ForeignKey("customers.id"), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    merchant_or_description = Column(String, nullable=False)
    category = Column(String, nullable=False, index=True)  # GROCERIES, DINING, UTILITIES, SALARY, SHOPPING, TRAVEL, ENTERTAINMENT, HEALTHCARE, INVESTMENTS
    amount = Column(Float, nullable=False)
    direction = Column(String, nullable=False)  # DEBIT, CREDIT
    status = Column(String, default="COMPLETED")  # COMPLETED, PENDING, FAILED
    reference_number = Column(String, nullable=True)

    # Relationships
    account = relationship("Account", back_populates="transactions")
    customer = relationship("Customer", back_populates="transactions")
