from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.database.init_db import init_db
from app.api import (
    auth,
    dashboard,
    accounts,
    transactions,
    insights,
    products,
    loans,
    chat,
    evaluation,
    health
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Idempotent DB initialization on startup
    init_db()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="NexaBank AI — Banking Customer Query Assistant with controlled tool-calling, multi-customer isolation, and deterministic loan calculations. Built for TCS Technology Day.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enforce explicit CORS allowlist
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept", "Origin", "X-Requested-With"],
)

# Register API routers under /api
app.include_router(health.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(accounts.router, prefix="/api")
app.include_router(transactions.router, prefix="/api")
app.include_router(insights.router, prefix="/api")
app.include_router(products.router, prefix="/api")
app.include_router(loans.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(evaluation.router, prefix="/api")

@app.get("/")
def root():
    return {
        "message": "Welcome to NexaBank AI Banking Assistant API",
        "demo_mode": settings.DEMO_MODE,
        "docs": "/docs",
        "health": "/api/health"
    }
