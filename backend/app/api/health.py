from datetime import datetime, timezone
from fastapi import APIRouter
from app.core.config import settings
from app.ai.gemini_client import is_gemini_available

router = APIRouter(tags=["Health & Status"])

@router.get("/health")
def health_check():
    return {
        "status": "operational",
        "app_name": settings.PROJECT_NAME,
        "demo_mode": settings.DEMO_MODE,
        "database": "sqlite_connected",
        "gemini_ai_configured": is_gemini_available(),
        "ai_engine_mode": "gemini-llm" if is_gemini_available() else "deterministic-fallback",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
