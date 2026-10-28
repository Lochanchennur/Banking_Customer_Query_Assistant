from typing import Dict, Any, List

TOOL_DEFINITIONS = [
    {
        "name": "get_account_balance",
        "description": "Retrieve current ledger balance and available balance across all accounts or for a specific account type (e.g., CHECKING, SAVINGS).",
        "parameters": {
            "type": "object",
            "properties": {
                "account_type": {
                    "type": "string",
                    "description": "Optional account type filter: 'CHECKING', 'SAVINGS', or 'INVESTMENT'"
                }
            }
        }
    },
    {
        "name": "get_accounts",
        "description": "List all active banking accounts belonging to the customer with masked account numbers.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "get_transactions",
        "description": "Retrieve recent financial transactions from the database with optional filtering by count, category, or debit/credit direction.",
        "parameters": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Number of transactions to return (e.g. 5 for 'last five transactions', default 5, max 20)"
                },
                "category": {
                    "type": "string",
                    "description": "Optional category filter: 'DINING', 'GROCERIES', 'UTILITIES', 'SHOPPING', 'TRAVEL', 'SALARY', 'ENTERTAINMENT', 'HEALTHCARE'"
                },
                "direction": {
                    "type": "string",
                    "description": "Optional direction: 'DEBIT' or 'CREDIT'"
                }
            }
        }
    },
    {
        "name": "calculate_spending_summary",
        "description": "Calculate verified total spending and category breakdown from matching database transaction records.",
        "parameters": {
            "type": "object",
            "properties": {
                "period": {
                    "type": "string",
                    "description": "Time period: 'this_month', 'last_month', or 'all'",
                    "enum": ["this_month", "last_month", "all"]
                },
                "category": {
                    "type": "string",
                    "description": "Optional category name (e.g. 'food', 'groceries', 'utilities', 'shopping')"
                }
            }
        }
    },
    {
        "name": "get_product_rates",
        "description": "Retrieve current official interest rates and terms for NexaBank products (personal loans, home loans, fixed deposits, savings accounts).",
        "parameters": {
            "type": "object",
            "properties": {
                "product_type": {
                    "type": "string",
                    "description": "Optional filter: 'PERSONAL_LOAN', 'HOME_LOAN', 'FIXED_DEPOSIT', 'SAVINGS_ACCOUNT'"
                }
            }
        }
    },
    {
        "name": "check_mock_loan_eligibility",
        "description": "Evaluate indicative personal loan or home loan eligibility using deterministic risk rules.",
        "parameters": {
            "type": "object",
            "properties": {
                "loan_type": {
                    "type": "string",
                    "description": "'PERSONAL_LOAN' or 'HOME_LOAN'"
                },
                "requested_amount": {
                    "type": "number",
                    "description": "Requested principal amount in INR (e.g., 500000)"
                },
                "tenure_months": {
                    "type": "integer",
                    "description": "Requested repayment tenure in months (e.g. 36)"
                }
            },
            "required": ["requested_amount"]
        }
    },
    {
        "name": "search_banking_faq",
        "description": "Search the NexaBank knowledge base for banking procedures, policies, statement downloads, card controls, or UPI limits.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search keywords or customer question"
                }
            },
            "required": ["query"]
        }
    }
]

def sanitize_tool_args(tool_name: str, raw_args: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and sanitize tool parameters to guard against prompt injection or malformed payloads."""
    clean_args: Dict[str, Any] = {}
    
    if tool_name == "get_account_balance":
        acc_type = raw_args.get("account_type")
        if acc_type and isinstance(acc_type, str):
            clean_args["account_type"] = acc_type[:30]
            
    elif tool_name == "get_transactions":
        limit = raw_args.get("limit", 5)
        try:
            clean_args["limit"] = max(1, min(int(limit), 20))
        except (ValueError, TypeError):
            clean_args["limit"] = 5
        
        category = raw_args.get("category")
        if category and isinstance(category, str):
            clean_args["category"] = category[:30]
            
        direction = raw_args.get("direction")
        if direction and isinstance(direction, str) and direction.upper() in ["DEBIT", "CREDIT"]:
            clean_args["direction"] = direction.upper()

    elif tool_name == "calculate_spending_summary":
        period = raw_args.get("period", "last_month")
        if period in ["this_month", "last_month", "all"]:
            clean_args["period"] = period
        else:
            clean_args["period"] = "last_month"
            
        category = raw_args.get("category")
        if category and isinstance(category, str):
            clean_args["category"] = category[:30]

    elif tool_name == "get_product_rates":
        p_type = raw_args.get("product_type")
        if p_type and isinstance(p_type, str):
            clean_args["product_type"] = p_type[:30]

    elif tool_name == "check_mock_loan_eligibility":
        try:
            clean_args["requested_amount"] = float(raw_args.get("requested_amount", 500000))
        except (ValueError, TypeError):
            clean_args["requested_amount"] = 500000.0
        
        try:
            clean_args["tenure_months"] = int(raw_args.get("tenure_months", 36))
        except (ValueError, TypeError):
            clean_args["tenure_months"] = 36
            
        loan_type = raw_args.get("loan_type", "PERSONAL_LOAN")
        clean_args["loan_type"] = "HOME_LOAN" if "home" in str(loan_type).lower() else "PERSONAL_LOAN"

    elif tool_name == "search_banking_faq":
        query = raw_args.get("query", "")
        clean_args["query"] = str(query)[:100]

    return clean_args
