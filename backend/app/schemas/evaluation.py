from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class EvalTestCase(BaseModel):
    id: str
    category: str
    query: str
    expected_intent: str
    expected_tools: List[str]
    should_succeed: bool = True
    security_flag: bool = False

class EvalResultItem(BaseModel):
    id: str
    category: str
    query: str
    expected_intent: str
    actual_intent: str
    expected_tools: List[str]
    actual_tools: List[str]
    intent_match: bool
    tool_match: bool
    financial_data_accurate: bool
    success: bool
    latency_ms: float
    reply_snippet: str
    source: str
    security_passed: bool

class EvalSummary(BaseModel):
    total_queries: int
    passed_queries: int
    resolution_accuracy_pct: float
    tool_selection_accuracy_pct: float
    financial_data_accuracy_pct: float
    security_pass_rate_pct: float
    median_latency_ms: float
    p95_latency_ms: float
    max_latency_ms: float
    error_rate_pct: float
    category_breakdown: Dict[str, Dict[str, Any]]
    results: List[EvalResultItem]
    timestamp: str
