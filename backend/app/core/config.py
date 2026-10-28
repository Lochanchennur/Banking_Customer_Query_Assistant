import os
import secrets
from typing import List
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

def get_secure_jwt_secret() -> str:
    """
    Remove insecure default JWT secrets.
    Enforce high-entropy 256-bit secret key.
    Rejects trivial or default strings in production.
    """
    env_secret = os.getenv("SECRET_KEY", "").strip()
    weak_defaults = {"secret", "demo", "changeme", "default", "password", "nexabank-demo-secret-key-32-chars-minimum-safe-for-eval"}
    env_name = os.getenv("ENVIRONMENT", "development").lower()

    if env_secret and env_secret not in weak_defaults and len(env_secret) >= 32:
        return env_secret

    if env_name == "production":
        raise ValueError(
            "CRITICAL SECURITY CONFIGURATION ERROR: SECRET_KEY must be explicitly set to a 32+ character high-entropy key in production."
        )

    # In development/test, maintain a persistent generated secret file or generate dynamic high-entropy key
    secret_path = os.path.join(os.path.dirname(__file__), "..", "..", ".jwt_secret")
    if os.path.exists(secret_path):
        try:
            with open(secret_path, "r", encoding="utf-8") as f:
                saved = f.read().strip()
                if len(saved) >= 32:
                    return saved
        except Exception:
            pass

    generated = secrets.token_hex(32)
    try:
        with open(secret_path, "w", encoding="utf-8") as f:
            f.write(generated)
    except Exception:
        pass
    return generated

def get_cors_origins() -> List[str]:
    raw = os.getenv("CORS_ORIGINS", "")
    if raw.strip():
        return [o.strip() for o in raw.split(",") if o.strip()]
    return [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]

class Settings(BaseModel):
    PROJECT_NAME: str = "NexaBank AI — Banking Customer Query Assistant"
    API_V1_STR: str = "/api"
    SECRET_KEY: str = Field(default_factory=get_secure_jwt_secret)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./nexabank.db")
    DEMO_MODE: bool = os.getenv("DEMO_MODE", "true").lower() == "true"
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    CORS_ORIGINS: List[str] = Field(default_factory=get_cors_origins)

settings = Settings()

