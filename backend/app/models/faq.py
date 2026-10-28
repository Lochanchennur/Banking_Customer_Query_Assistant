from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime
from app.database.session import Base

class FAQ(Base):
    __tablename__ = "faqs"

    id = Column(String, primary_key=True, index=True)
    category = Column(String, nullable=False, index=True)
    question = Column(String, nullable=False)
    answer = Column(String, nullable=False)
    keywords = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
