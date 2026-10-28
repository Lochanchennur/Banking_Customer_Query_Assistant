import json
import logging
from typing import Dict, Any, Optional, List, Tuple
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.customer import Customer
from app.ai.tool_registry import TOOL_DEFINITIONS, sanitize_tool_args
from app.ai.tools import TOOL_MAPPING

logger = logging.getLogger(__name__)

def is_gemini_available() -> bool:
    return bool(settings.GEMINI_API_KEY and len(settings.GEMINI_API_KEY.strip()) > 5)

def get_genai_tools():
    """Convert TOOL_DEFINITIONS into google.genai Tool object."""
    from google.genai import types
    fds = []
    for td in TOOL_DEFINITIONS:
        fd = types.FunctionDeclaration(
            name=td["name"],
            description=td["description"],
            parameters=td["parameters"]
        )
        fds.append(fd)
    return [types.Tool(function_declarations=fds)]

def execute_gemini_with_function_calling(
    db: Session,
    customer: Customer,
    system_prompt: str,
    user_message: str,
    history: Optional[List[Dict[str, str]]] = None
) -> Optional[Dict[str, Any]]:
    """
    Execute Gemini LLM with true Function Calling (Tool Selection & Invocation):
    1. Send prompt with banking tool declarations to Gemini.
    2. If Gemini requests one or more tool calls:
       - Validate tool name against server-side whitelist.
       - Sanitize arguments.
       - Execute server-side tool against verified SQLite database.
       - Package tool results into FunctionResponse parts.
       - Return tool outputs to Gemini for final grounded natural language generation.
    3. If Gemini responds without tool calls, return conversational response.
    4. Return structured metadata, executed tools, and disclaimer for UI widgets.
    """
    if not is_gemini_available():
        return None

    try:
        from google.genai import types
        from google.genai import Client

        client = Client(api_key=settings.GEMINI_API_KEY)
        genai_tools = get_genai_tools()

        config = types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.1,
            tools=genai_tools
        )

        # Build conversation history
        contents = []
        if history:
            for h in history[-4:]:
                role = "user" if h.get("role") == "user" else "model"
                contents.append(types.Content(role=role, parts=[types.Part.from_text(text=h.get("content", ""))]))

        contents.append(types.Content(role="user", parts=[types.Part.from_text(text=user_message)]))

        # First turn: Gemini selects tool(s)
        logger.info(f"Invoking Gemini with tool declarations for query: {user_message[:50]}...")
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=contents,
            config=config
        )

        # Check if Gemini selected functions to call
        function_calls = getattr(response, "function_calls", None)

        if not function_calls and response.candidates:
            # Check candidate content parts
            candidate = response.candidates[0]
            if candidate.content and candidate.content.parts:
                for part in candidate.content.parts:
                    if getattr(part, "function_call", None):
                        if function_calls is None:
                            function_calls = []
                        function_calls.append(part.function_call)

        # Case A: Gemini requested tool execution(s)
        if function_calls:
            logger.info(f"Gemini selected {len(function_calls)} tool call(s): {[c.name for c in function_calls]}")
            tools_executed = []
            structured_data: Dict[str, Any] = {}
            tool_response_parts = []
            intents = []
            has_loan_query = False

            # Append the model's function_call turn to history
            if response.candidates and response.candidates[0].content:
                contents.append(response.candidates[0].content)

            for call in function_calls:
                call_name = getattr(call, "name", "")
                raw_args = getattr(call, "args", {}) or {}
                if isinstance(raw_args, str):
                    try:
                        raw_args = json.loads(raw_args)
                    except Exception:
                        raw_args = {}

                if call_name not in TOOL_MAPPING:
                    logger.warning(f"Gemini requested unapproved tool: {call_name}. Rejecting.")
                    tool_result = {"status": "error", "message": f"Tool '{call_name}' is not authorized."}
                else:
                    # Validate & sanitize arguments
                    clean_args = sanitize_tool_args(call_name, raw_args)
                    logger.info(f"Executing server tool '{call_name}' with verified args {clean_args}")
                    
                    # Execute tool against verified banking service
                    tool_result = TOOL_MAPPING[call_name](db, customer, **clean_args)

                    # Extract structured data for frontend UI components
                    if call_name == "get_account_balance":
                        intents.append("ACCOUNT_BALANCE")
                        structured_data["accounts"] = tool_result.get("accounts", tool_result.get("all_accounts", []))
                    elif call_name == "get_accounts":
                        intents.append("LIST_ACCOUNTS")
                        structured_data["accounts"] = tool_result.get("accounts", [])
                    elif call_name == "get_transactions":
                        intents.append("TRANSACTION_HISTORY")
                        structured_data["transactions"] = tool_result.get("transactions", [])
                    elif call_name == "calculate_spending_summary":
                        intents.append("SPENDING_INSIGHTS")
                        if "matching_transactions" in tool_result:
                            structured_data["transactions"] = tool_result.get("matching_transactions", [])
                        structured_data["spending_summary"] = {
                            "period": tool_result.get("period"),
                            "total_spent": tool_result.get("category_total_spent", tool_result.get("total_spent", 0)),
                            "by_category": tool_result.get("by_category", tool_result.get("all_categories", []))
                        }
                    elif call_name == "check_mock_loan_eligibility":
                        intents.append("LOAN_ELIGIBILITY")
                        has_loan_query = True
                        structured_data["loan_eligibility"] = tool_result.get("eligibility_result", {})
                    elif call_name == "get_product_rates":
                        intents.append("PRODUCT_RATES")
                        structured_data["products"] = tool_result.get("products", [])
                    elif call_name == "search_banking_faq":
                        intents.append("BANKING_FAQ")
                        structured_data["faqs"] = tool_result.get("matches", [])

                tools_executed.append({
                    "tool_name": call_name,
                    "arguments": raw_args,
                    "status": "success" if tool_result.get("status") == "success" else "error",
                    "result_summary": f"Executed server tool {call_name}"
                })

                # Construct function response part for Gemini
                tool_part = types.Part.from_function_response(
                    name=call_name,
                    response={"result": tool_result}
                )
                tool_response_parts.append(tool_part)

            # Second turn: Pass verified ground truth back to Gemini
            contents.append(types.Content(role="user", parts=tool_response_parts))
            
            final_turn_response = client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=contents,
                config=config
            )

            final_reply = ""
            if final_turn_response and final_turn_response.text:
                final_reply = final_turn_response.text

            final_intent = "COMPOUND_QUERY" if len(intents) > 1 else (intents[0] if intents else "GENERAL_QUERY")
            disclaimer = "Illustrative demonstration calculation only. Not an actual credit decision or binding financial offer." if has_loan_query else None

            return {
                "reply": final_reply,
                "intent": final_intent,
                "tools_executed": tools_executed,
                "structured_data": structured_data if structured_data else None,
                "disclaimer": disclaimer,
                "source": "gemini-llm"
            }

        # Case B: Gemini answered directly without calling tools
        if response and response.text:
            return {
                "reply": response.text,
                "intent": "CONVERSATIONAL",
                "tools_executed": [],
                "structured_data": None,
                "disclaimer": None,
                "source": "gemini-llm"
            }

    except Exception as e:
        logger.warning(f"Gemini function-calling request encountered error: {e}. Falling back to deterministic engine.")
        return None

    return None
