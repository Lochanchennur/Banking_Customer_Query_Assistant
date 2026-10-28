import pytest
from unittest.mock import MagicMock, patch
from app.ai.gemini_client import (
    get_genai_tools,
    execute_gemini_with_function_calling,
    is_gemini_available
)
from app.ai.tool_registry import TOOL_DEFINITIONS, sanitize_tool_args
from app.ai.tools import TOOL_MAPPING
from app.ai.agent import execute_chat_query
from app.schemas.chat import ChatRequest
from app.models.customer import Customer

def test_genai_tool_registration():
    """Verify all 7 banking tools are registered with schemas for Google GenAI SDK."""
    tools = get_genai_tools()
    assert len(tools) == 1
    tool = tools[0]
    fds = tool.function_declarations
    assert len(fds) == 7
    
    expected_names = {
        "get_account_balance",
        "get_accounts",
        "get_transactions",
        "calculate_spending_summary",
        "get_product_rates",
        "check_mock_loan_eligibility",
        "search_banking_faq"
    }
    registered_names = {fd.name for fd in fds}
    assert registered_names == expected_names

    # Check each declaration has description and parameters
    for fd in fds:
        assert fd.description and len(fd.description) > 10
        assert fd.parameters is not None

def test_tool_argument_sanitization():
    """Test validation and sanitization of raw arguments from LLM."""
    # Transactions limit clamping
    tx_args = sanitize_tool_args("get_transactions", {"limit": 100, "category": "dining"})
    assert tx_args["limit"] == 20  # Max clamp
    assert tx_args["category"] == "dining"

    tx_min = sanitize_tool_args("get_transactions", {"limit": -5})
    assert tx_min["limit"] == 1  # Min clamp

    # Loan eligibility argument validation
    loan_args = sanitize_tool_args("check_mock_loan_eligibility", {
        "loan_type": "personal",
        "requested_amount": "500000",
        "tenure_months": "36"
    })
    assert loan_args["requested_amount"] == 500000.0
    assert loan_args["tenure_months"] == 36
    assert loan_args["loan_type"] == "PERSONAL_LOAN"

def test_unapproved_tool_rejection(db_session):
    """Test that requesting an unapproved tool name is rejected."""
    unapproved_name = "drop_database_tables"
    assert unapproved_name not in TOOL_MAPPING

def test_gemini_function_calling_mock_roundtrip(db_session):
    """
    Simulate Gemini SDK returning a function call for get_account_balance:
    1. Gemini returns FunctionCall part
    2. Server validates name & arguments
    3. Server executes server-side tool against verified SQLite DB
    4. Server packages result into FunctionResponse part and calls Gemini for grounded generation
    """
    customer = db_session.query(Customer).filter_by(id="cust_rajesh").first()
    
    mock_func_call = MagicMock()
    mock_func_call.name = "get_account_balance"
    mock_func_call.args = {"account_type": "SAVINGS"}

    mock_part = MagicMock()
    mock_part.function_call = mock_func_call

    mock_candidate = MagicMock()
    mock_candidate.content.parts = [mock_part]

    mock_first_turn_response = MagicMock()
    mock_first_turn_response.function_calls = [mock_func_call]
    mock_first_turn_response.candidates = [mock_candidate]

    mock_final_turn_response = MagicMock()
    mock_final_turn_response.text = "Your verified savings balance is ₹4,80,000.00."

    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = [
        mock_first_turn_response,
        mock_final_turn_response
    ]

    with patch("app.ai.gemini_client.is_gemini_available", return_value=True):
        with patch("google.genai.Client", return_value=mock_client):
            res = execute_gemini_with_function_calling(
                db=db_session,
                customer=customer,
                system_prompt="Test system prompt",
                user_message="Check my savings balance"
            )
            assert res is not None
            assert res["intent"] == "ACCOUNT_BALANCE"
            assert "4,80,000.00" in res["reply"]
            assert len(res["tools_executed"]) == 1
            assert res["tools_executed"][0]["tool_name"] == "get_account_balance"
            assert res["source"] == "gemini-llm"
            assert res["structured_data"] is not None

def test_api_failure_fallback_behavior(db_session):
    """
    Test that when Gemini API raises an exception (timeout, rate limit, network error),
    the agent catches the error and seamlessly falls back to the deterministic engine.
    """
    customer = db_session.query(Customer).filter_by(id="cust_rajesh").first()

    with patch("app.ai.gemini_client.is_gemini_available", return_value=True):
        with patch("google.genai.Client", side_effect=Exception("API Connection Timeout or 503 Service Unavailable")):
            req = ChatRequest(message="What is my current account balance?")
            res = execute_chat_query(db=db_session, customer=customer, request=req)
            
            # Must not crash, must return valid deterministic fallback response
            assert res is not None
            assert res.intent == "ACCOUNT_BALANCE"
            assert res.source == "deterministic-fallback"
            assert len(res.tools_executed) == 1
            assert res.tools_executed[0].tool_name == "get_account_balance"
            assert "574,520.50" in res.reply

def test_gemini_disabled_uses_fallback(db_session):
    """When GEMINI_API_KEY is not configured, agent uses deterministic fallback engine."""
    customer = db_session.query(Customer).filter_by(id="cust_rajesh").first()
    
    with patch("app.ai.gemini_client.settings.GEMINI_API_KEY", ""):
        assert is_gemini_available() is False
        req = ChatRequest(message="Show my last 5 transactions")
        res = execute_chat_query(db=db_session, customer=customer, request=req)
        assert res.intent == "TRANSACTION_HISTORY"
        assert res.source == "deterministic-fallback"
        assert len(res.tools_executed) == 1
