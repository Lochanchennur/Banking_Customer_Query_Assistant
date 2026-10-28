import re
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from app.models.customer import Customer
from app.ai.tools import (
    tool_get_account_balance,
    tool_get_transactions,
    tool_calculate_spending_summary,
    tool_get_product_rates,
    tool_check_mock_loan_eligibility,
    tool_search_banking_faq,
    tool_get_accounts
)

RE_BALANCE = re.compile(r'\b(balance|money\s+(do\s+i\s+have|in\s+my)|cash|funds?|how\s+much(\s+\w+)?\s+(do\s+i\s+have|in\s+my\s+account)|available\s+funds|sitting\s+in\s+my\s+account)\b', re.I)
RE_TRANSACTIONS = re.compile(r'\b(transactions?|history|recent\s+(payments?|activity|charges?)|last\s+(\d+|five|ten|three)?\s*transactions?)\b', re.I)
RE_SPENDING = re.compile(r'\b(spend|spending|spent|expenses?|expenditure|blow\s+on|paid\s+for|how\s+much\s+(did\s+i\s+spend|was\s+spent))\b', re.I)
RE_RATES = re.compile(r'\b(interest\s*rates?|rates?|cost\s+of\s+borrowing|mortgage\s+rate|what\s+is\s+the\s+rate|loan\s+rate|fd\s+rate|roi)\b', re.I)
RE_ELIGIBILITY = re.compile(r'\b(eligible|eligibility|meet\s+criteria|criteria\s+for|personal\s+credit|can\s+i\s+(get|apply\s+for)\s+(a\s+)?(personal\s+|home\s+)?loan|apply\s+for\s+(a\s+)?(personal\s+|home\s+)?loan|qualify)\b', re.I)
RE_ACCOUNTS = re.compile(r'\b(my\s+accounts|list\s+accounts|which\s+accounts|account\s+numbers?)\b', re.I)
RE_FAQ = re.compile(r'\b(how\s+(do|can|often)\s+i|how\s+often|download|statement|pin|freeze|block|limit|upi|neft|clearance|tax\s+certificate|calculated|credited)\b', re.I)

RE_INJECTION = re.compile(
    r'(ignore\s+(all\s+)?(previous|prior)\s+instructions|system\s+prompt|bypass|drop\s+table|select\s+.*\s+from|delete\s+from|insert\s+into|union\s+select|;\s*drop|;\s*delete|;\s*update|reveal\s+all|other\s+customers|admin\s+mode|--|\bexec\s*\()',
    re.I
)

def detect_prompt_injection(message: str) -> bool:
    """Detect prompt injection and SQL injection patterns in user query."""
    return bool(RE_INJECTION.search(message))

def check_security_violation(customer: Customer, message: str) -> Optional[str]:
    """
    Enforce security guardrails:
    1. Prompt injection & SQL injection defense
    2. Cross-customer data isolation & unauthorized account probing
    """
    clean_msg = message.strip()
    if detect_prompt_injection(clean_msg):
        return "Prompt injection or SQL injection pattern detected."

    msg_lower = clean_msg.lower()
    
    # Cross-customer access prevention
    other_targets = []
    if customer.id == "cust_rajesh":
        other_targets = ["priya", "vikram", "acc_priya", "acc_vikram"]
    elif customer.id == "cust_priya":
        other_targets = ["rajesh", "vikram", "acc_rajesh", "acc_vikram"]
    elif customer.id == "cust_vikram":
        other_targets = ["rajesh", "priya", "acc_rajesh", "acc_priya"]

    for target in other_targets:
        if target in msg_lower:
            return f"Unauthorized cross-customer access attempt for '{target}' blocked."

    if any(phrase in msg_lower for phrase in [
        "other customer", "another customer", "someone else's", "all customers", "other account"
    ]):
        return "Unauthorized multi-tenant cross-customer access blocked."

    return None

def process_deterministic_query(
    db: Session,
    customer: Customer,
    message: str
) -> Dict[str, Any]:
    """
    High-precision deterministic rule engine.
    Supports single and compound banking queries, date resolution, and security guardrails.
    """
    clean_msg = message.strip()
    
    # 1. Enforce security guardrails
    violation = check_security_violation(customer, clean_msg)
    if violation:
        return {
            "reply": "Security Notice: I cannot fulfill this request. In accordance with NexaBank security policies, banking assistant sessions are strictly isolated to authenticated customer operations and protected against system prompt modifications or unauthorized cross-customer queries.",
            "intent": "SECURITY_ALERT",
            "tools_executed": [],
            "structured_data": None,
            "source": "deterministic-fallback",
            "disclaimer": "Security boundary enforcement active."
        }

    tools_executed = []
    structured_data: Dict[str, Any] = {}
    reply_parts = []
    intents = []

    # Check for compound query: Balance + Spending or Balance + Transactions
    is_compound = False
    
    # Check Balance intent
    if RE_BALANCE.search(clean_msg):
        intents.append("ACCOUNT_BALANCE")
        acc_type = None
        if "saving" in clean_msg.lower():
            acc_type = "SAVINGS"
        elif "checking" in clean_msg.lower() or "salary" in clean_msg.lower():
            acc_type = "CHECKING"
            
        bal_res = tool_get_account_balance(db, customer, account_type=acc_type)
        tools_executed.append({
            "tool_name": "get_account_balance",
            "arguments": {"account_type": acc_type},
            "status": "success",
            "result_summary": f"Retrieved balance ₹{bal_res.get('balance', bal_res.get('total_balance', 0)):,.2f}"
        })
        structured_data["accounts"] = bal_res.get("accounts", bal_res.get("all_accounts", []))
        
        if acc_type and "balance" in bal_res:
            reply_parts.append(
                f"Your **{acc_type.capitalize()} Account** ({bal_res.get('account_masked')}) has a current balance of **₹{bal_res['balance']:,.2f}** (Available: **₹{bal_res['available_balance']:,.2f}**)."
            )
        else:
            total_bal = bal_res.get("total_balance", 0.0)
            avail_bal = bal_res.get("total_available_balance", 0.0)
            acc_count = bal_res.get("account_count", 0)
            reply_parts.append(
                f"Your total balance across **{acc_count} accounts** is **₹{total_bal:,.2f}** (Available balance: **₹{avail_bal:,.2f}**)."
            )

    # Check Spending intent
    if RE_SPENDING.search(clean_msg):
        intents.append("SPENDING_INSIGHTS")
        period = "last_month" if "last month" in clean_msg.lower() or "previous month" in clean_msg.lower() else "this_month"
        
        # Check category
        category = None
        for cat_name in ["food", "groceries", "dining", "restaurant", "restaurants", "utility", "utilities", "bills", "shopping", "travel", "entertainment", "healthcare"]:
            if cat_name in clean_msg.lower():
                category = cat_name
                break
                
        spend_res = tool_calculate_spending_summary(db, customer, period=period, category=category)
        tools_executed.append({
            "tool_name": "calculate_spending_summary",
            "arguments": {"period": period, "category": category},
            "status": "success",
            "result_summary": f"Calculated spending for {period}"
        })
        
        period_label = "last month" if period == "last_month" else "this month"
        if category:
            cat_spent = spend_res.get("category_total_spent", 0.0)
            structured_data["transactions"] = spend_res.get("matching_transactions", [])
            structured_data["spending_summary"] = {
                "period": period_label,
                "category": category,
                "amount": cat_spent,
                "total_spent": cat_spent,
                "matching_count": len(spend_res.get("matching_transactions", []))
            }
            reply_parts.append(
                f"You spent a verified total of **₹{cat_spent:,.2f}** on **{category}** during {period_label} across {len(spend_res.get('matching_transactions', []))} transactions."
            )
        else:
            tot_spent = spend_res.get("total_spent", 0.0)
            tot_inc = spend_res.get("total_income", 0.0)
            structured_data["spending_summary"] = {
                "period": period_label,
                "total_spent": tot_spent,
                "total_income": tot_inc,
                "by_category": spend_res.get("by_category", [])
            }
            reply_parts.append(
                f"During {period_label}, your total debits were **₹{tot_spent:,.2f}** against total income of **₹{tot_inc:,.2f}**."
            )

    # Check Transactions intent (if not already handled via spending category)
    if RE_TRANSACTIONS.search(clean_msg) and not (RE_SPENDING.search(clean_msg) and "food" in clean_msg.lower()):
        intents.append("TRANSACTION_HISTORY")
        # Extract limit (default 5)
        limit = 5
        match_digits = re.search(r'\b(\d+)\b', clean_msg)
        if match_digits:
            limit = int(match_digits.group(1))
        elif "five" in clean_msg.lower():
            limit = 5
        elif "ten" in clean_msg.lower():
            limit = 10
        elif "three" in clean_msg.lower():
            limit = 3

        txn_res = tool_get_transactions(db, customer, limit=limit)
        tools_executed.append({
            "tool_name": "get_transactions",
            "arguments": {"limit": limit},
            "status": "success",
            "result_summary": f"Found {len(txn_res.get('transactions', []))} records"
        })
        structured_data["transactions"] = txn_res.get("transactions", [])
        txns_list = txn_res.get("transactions", [])
        
        reply_parts.append(
            f"Here are your last **{len(txns_list)} transactions** from your verified account ledger:"
        )

    # Check Loan Eligibility intent
    if RE_ELIGIBILITY.search(clean_msg):
        intents.append("LOAN_ELIGIBILITY")
        loan_type = "HOME_LOAN" if "home" in clean_msg.lower() else "PERSONAL_LOAN"
        
        # Check if amount mentioned
        amount = 500000.0
        amt_match = re.search(r'(\d+)\s*(lakh|lakhs|lac|lacs|k|thousand)?', clean_msg, re.I)
        if amt_match:
            val = float(amt_match.group(1))
            unit = (amt_match.group(2) or "").lower()
            if "lakh" in unit or "lac" in unit:
                amount = val * 100000.0
            elif "k" in unit or "thousand" in unit:
                amount = val * 1000.0
            elif val > 1000:
                amount = val

        elig_res = tool_check_mock_loan_eligibility(db, customer, loan_type=loan_type, requested_amount=amount)
        tools_executed.append({
            "tool_name": "check_mock_loan_eligibility",
            "arguments": {"loan_type": loan_type, "requested_amount": amount},
            "status": "success",
            "result_summary": f"Status: {elig_res['eligibility_result']['status']}"
        })
        
        result_details = elig_res["eligibility_result"]
        structured_data["loan_eligibility"] = result_details
        
        status_text = "Approved (Indicative)" if result_details["eligible"] else "Not Recommended at this stage"
        reply_parts.append(
            f"### Indicative Loan Assessment\n"
            f"**Product**: {result_details['product_type'].replace('_', ' ').title()}\n"
            f"**Indicative Status**: **{status_text}**\n"
            f"**Requested Principal**: ₹{result_details['requested_amount']:,.2f}\n"
            f"**Eligible Limit**: ₹{result_details['approved_amount']:,.2f}\n"
            f"**Applicable Rate**: {result_details['interest_rate']}% p.a. (Tenure: {result_details['tenure_months']} months)\n"
            f"**Estimated Monthly EMI**: ₹{result_details['estimated_emi']:,.2f}\n\n"
            f"**Evaluation**: {result_details['reason']}"
        )

    # Check Product Rates intent
    if RE_RATES.search(clean_msg):
        intents.append("PRODUCT_RATES")
        p_filter = None
        if "home" in clean_msg.lower():
            p_filter = "HOME_LOAN"
        elif "personal" in clean_msg.lower():
            p_filter = "PERSONAL_LOAN"
        elif "fd" in clean_msg.lower() or "deposit" in clean_msg.lower():
            p_filter = "FIXED_DEPOSIT"
        elif "savings" in clean_msg.lower():
            p_filter = "SAVINGS_ACCOUNT"

        rates_res = tool_get_product_rates(db, customer, product_type=p_filter)
        tools_executed.append({
            "tool_name": "get_product_rates",
            "arguments": {"product_type": p_filter},
            "status": "success",
            "result_summary": f"Fetched {len(rates_res.get('products', []))} products"
        })
        structured_data["products"] = rates_res.get("products", [])
        
        prods = rates_res.get("products", [])
        rate_lines = [f"- **{p['name']}**: **{p['interest_rate']}% p.a.** ({p['rate_type']}) — {p['headline']}" for p in prods]
        reply_parts.append(
            f"Here are current NexaBank interest rates:\n" + "\n".join(rate_lines)
        )

    # Check Accounts intent
    if RE_ACCOUNTS.search(clean_msg) and "ACCOUNT_BALANCE" not in intents:
        intents.append("LIST_ACCOUNTS")
        acc_res = tool_get_accounts(db, customer)
        tools_executed.append({
            "tool_name": "get_accounts",
            "arguments": {},
            "status": "success",
            "result_summary": f"Found {len(acc_res.get('accounts', []))} accounts"
        })
        structured_data["accounts"] = acc_res.get("accounts", [])
        lines = [f"- **{a['account_name']}** ({a['account_number_masked']}): Balance ₹{a['balance']:,.2f} ({a['status']})" for a in acc_res.get("accounts", [])]
        reply_parts.append("Here are your active NexaBank accounts:\n" + "\n".join(lines))

    # Check FAQ intent
    if RE_FAQ.search(clean_msg) and not intents:
        faq_res = tool_search_banking_faq(db, customer, query=clean_msg)
        matches = faq_res.get("matches", [])
        if matches:
            intents.append("BANKING_FAQ")
            tools_executed.append({
                "tool_name": "search_banking_faq",
                "arguments": {"query": clean_msg},
                "status": "success",
                "result_summary": f"Found {len(matches)} matching articles"
            })
            top = matches[0]
            structured_data["faqs"] = matches
            reply_parts.append(
                f"### {top['question']}\n{top['answer']}"
            )

    # If still empty (ambiguous or unrecognized question)
    if not reply_parts:
        return {
            "reply": "I am here to assist with your NexaBank accounts and services. You can ask me about:\n"
                     "- **Account Balances** (e.g., *'What is my current account balance?'*)\n"
                     "- **Recent Transactions** (e.g., *'Show my last five transactions'*)\n"
                     "- **Spending Summaries** (e.g., *'How much did I spend on food last month?'*)\n"
                     "- **Loans & Interest Rates** (e.g., *'What are the current home loan interest rates?'* or *'Am I eligible for a personal loan?'*)\n"
                     "- **Banking Procedures** (e.g., *'How do I download my monthly account statement?'*)\n\n"
                     "Could you please clarify your request?",
            "intent": "AMBIGUOUS_QUERY",
            "tools_executed": [],
            "structured_data": None,
            "source": "deterministic-fallback",
            "disclaimer": None
        }

    final_intent = "COMPOUND_QUERY" if len(intents) > 1 else (intents[0] if intents else "GENERAL_QUERY")
    final_reply = "\n\n".join(reply_parts)
    
    disclaimer = None
    if "LOAN_ELIGIBILITY" in intents:
        disclaimer = "Illustrative demonstration calculation only. Not an actual credit decision or binding financial offer."

    return {
        "reply": final_reply,
        "intent": final_intent,
        "tools_executed": tools_executed,
        "structured_data": structured_data if structured_data else None,
        "source": "deterministic-fallback",
        "disclaimer": disclaimer
    }
