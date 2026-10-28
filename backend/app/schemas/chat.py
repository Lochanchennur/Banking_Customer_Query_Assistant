from datetime import datetime
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: Optional[datetime] = None
    structured_data: Optional[Dict[str, Any]] = None

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    history: Optional[List[ChatMessage]] = []

class ToolExecutionRecord(BaseModel):
    tool_name: str
    arguments: Dict[str, Any]
    status: str
    result_summary: Optional[str] = None

class ChatResponse(BaseModel):
    message_id: str
    reply: str
    intent: str
    tools_executed: List[ToolExecutionRecord] = []
    structured_data: Optional[Dict[str, Any]] = None
    source: str = "deterministic-fallback"  # "gemini-llm" or "deterministic-fallback"
    latency_ms: float
    disclaimer: Optional[str] = None
