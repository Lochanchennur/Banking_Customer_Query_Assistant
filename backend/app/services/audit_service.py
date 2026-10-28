import uuid
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.audit import AuditEvent

def log_audit_event(
    db: Session,
    request_id: str,
    customer_id: Optional[str],
    intent: Optional[str],
    tools_called: Optional[List[str]],
    success: bool,
    latency_ms: float,
    source: str = "agent",
    status_code: str = "200"
) -> AuditEvent:
    tools_str = ",".join(tools_called) if tools_called else "none"
    event = AuditEvent(
        id=f"audit_{uuid.uuid4().hex[:12]}",
        request_id=request_id,
        timestamp=datetime.now(timezone.utc),
        customer_id=customer_id,
        intent=intent or "UNKNOWN",
        tools_called=tools_str,
        success=success,
        latency_ms=round(latency_ms, 2),
        source=source,
        status_code=status_code
    )
    db.add(event)
    try:
        db.commit()
    except Exception:
        db.rollback()
    return event

def get_recent_audit_events(db: Session, limit: int = 50) -> List[AuditEvent]:
    return db.query(AuditEvent).order_by(AuditEvent.timestamp.desc()).limit(limit).all()
