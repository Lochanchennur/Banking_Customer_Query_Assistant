from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Integer, DateTime
from app.database.session import Base

class BankingProduct(Base):
    __tablename__ = "banking_products"

    id = Column(String, primary_key=True, index=True)
    product_type = Column(String, nullable=False, index=True)  # PERSONAL_LOAN, HOME_LOAN, FIXED_DEPOSIT, SAVINGS_ACCOUNT, CAR_LOAN
    name = Column(String, nullable=False)
    headline = Column(String, nullable=False)
    interest_rate = Column(Float, nullable=False)  # e.g., 10.5 for 10.5%
    rate_type = Column(String, default="Fixed")    # Fixed or Floating
    min_amount = Column(Float, default=10000.0)
    max_amount = Column(Float, default=5000000.0)
    min_tenure_months = Column(Integer, default=6)
    max_tenure_months = Column(Integer, default=360)
    processing_fee_pct = Column(Float, default=1.0)
    eligibility_criteria_summary = Column(String, nullable=False)
    min_income_monthly = Column(Float, default=25000.0)
    min_credit_score = Column(Integer, default=650)
    effective_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
