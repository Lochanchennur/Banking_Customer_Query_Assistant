from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Boolean, DateTime
from app.database.session import Base

class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(String, primary_key=True, index=True)
    request_id = Column(String, index=True, nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    customer_id = Column(String, index=True, nullable=True)
    intent = Column(String, nullable=True)
    tools_called = Column(String, nullable=True)
    success = Column(Boolean, default=True)
    latency_ms = Column(Float, default=0.0)
    source = Column(String, default="agent")  # gemini-llm, deterministic-fallback, direct-api
    status_code = Column(String, default="200")
