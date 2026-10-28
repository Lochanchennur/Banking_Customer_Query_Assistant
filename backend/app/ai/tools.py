from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from app.models.customer import Customer
from app.models.product import BankingProduct
from app.services.banking_service import (
    get_customer_accounts,
    get_total_balance,
    get_customer_transactions,
    calculate_spending_insights,
    get_banking_products,
    search_faqs
)
from app.services.loan_calculator import evaluate_loan_eligibility

def tool_get_accounts(db: Session, customer: Customer, **kwargs) -> Dict[str, Any]:
    """Retrieve all active accounts for the authenticated customer."""
    accounts = get_customer_accounts(db, customer.id)
    return {
        "status": "success",
        "accounts_count": len(accounts),
        "accounts": [a.model_dump() for a in accounts]
    }

def tool_get_account_balance(db: Session, customer: Customer, account_type: Optional[str] = None, **kwargs) -> Dict[str, Any]:
    """Retrieve verified balance across accounts or for a specific account type."""
    summary = get_total_balance(db, customer.id)
    if account_type:
        filtered = [a for a in summary["accounts"] if a["type"].upper() == account_type.upper().strip()]
        if filtered:
            return {
                "status": "success",
                "customer_name": customer.name,
                "account_type": account_type.upper(),
                "balance": filtered[0]["balance"],
                "available_balance": filtered[0]["available"],
                "currency": summary["currency"],
                "account_masked": filtered[0]["masked"],
                "all_accounts": summary["accounts"]
            }
    
    return {
        "status": "success",
        "customer_name": customer.name,
        "total_balance": summary["total_balance"],
        "total_available_balance": summary["total_available_balance"],
        "currency": summary["currency"],
        "account_count": summary["account_count"],
        "accounts": summary["accounts"]
    }

def tool_get_transactions(
    db: Session,
    customer: Customer,
    account_id: Optional[str] = None,
    category: Optional[str] = None,
    direction: Optional[str] = None,
    limit: int = 5,
    **kwargs
) -> Dict[str, Any]:
    """Retrieve recent transaction history strictly for the authenticated customer."""
    safe_limit = max(1, min(int(limit), 20))
    resp = get_customer_transactions(
        db,
        customer_id=customer.id,
        account_id=account_id,
        category=category,
        direction=direction,
        limit=safe_limit
    )
    return {
        "status": "success",
        "total_matching_transactions": resp.total_count,
        "returned_count": len(resp.items),
        "total_debits": resp.total_debits,
        "total_credits": resp.total_credits,
        "transactions": [t.model_dump() for t in resp.items]
    }

def tool_calculate_spending_summary(
    db: Session,
    customer: Customer,
    period: str = "last_month",
    category: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """Calculate verified spending summaries from matching database records."""
    safe_period = period if period in ["this_month", "last_month", "all"] else "last_month"
    insights = calculate_spending_insights(db, customer.id, period=safe_period)
    
    # If specific category queried (e.g., "food")
    if category:
        cat_lower = category.lower().strip()
        matching_cats = [c for c in insights.by_category if cat_lower in c.category.lower() or (cat_lower == "food" and c.category in ["DINING", "GROCERIES"])]
        cat_spent = sum(c.amount for c in matching_cats)
        
        # Also fetch the matching transaction records for transparency
        txns_resp = get_customer_transactions(db, customer_id=customer.id, category=category, limit=10)
        return {
            "status": "success",
            "period": safe_period,
            "category_queried": category,
            "category_total_spent": round(cat_spent, 2),
            "currency": "INR",
            "matching_transactions": [t.model_dump() for t in txns_resp.items],
            "all_categories": [c.model_dump() for c in insights.by_category]
        }

    return {
        "status": "success",
        "period": safe_period,
        "total_spent": insights.total_spent,
        "total_income": insights.total_income,
        "net_savings": insights.net_savings,
        "currency": "INR",
        "by_category": [c.model_dump() for c in insights.by_category],
        "largest_expenses": [t.model_dump() for t in insights.largest_expenses]
    }

def tool_get_product_rates(db: Session, customer: Customer, product_type: Optional[str] = None, **kwargs) -> Dict[str, Any]:
    """Get active interest rates and specifications for banking products."""
    products = get_banking_products(db, product_type)
    return {
        "status": "success",
        "product_count": len(products),
        "products": [p.model_dump() for p in products]
    }

def tool_check_mock_loan_eligibility(
    db: Session,
    customer: Customer,
    loan_type: str = "PERSONAL_LOAN",
    requested_amount: float = 500000.0,
    tenure_months: int = 36,
    declared_monthly_income: Optional[float] = None,
    declared_existing_emis: Optional[float] = 0.0,
    **kwargs
) -> Dict[str, Any]:
    """Check loan eligibility using the deterministic rule engine."""
    p_type = "PERSONAL_LOAN" if "personal" in loan_type.lower() else "HOME_LOAN" if "home" in loan_type.lower() else "PERSONAL_LOAN"
    product = db.query(BankingProduct).filter(BankingProduct.product_type == p_type).first()
    if not product:
        return {"status": "error", "message": f"Product {loan_type} not found."}

    req_amt = float(requested_amount) if requested_amount else 500000.0
    tenure = int(tenure_months) if tenure_months else 36
    
    result = evaluate_loan_eligibility(
        customer=customer,
        product=product,
        requested_amount=req_amt,
        tenure_months=tenure,
        declared_monthly_income=declared_monthly_income,
        declared_existing_emis=declared_existing_emis or 0.0
    )
    return {
        "status": "success",
        "eligibility_result": result.model_dump()
    }

def tool_search_banking_faq(db: Session, customer: Customer, query: str = "", **kwargs) -> Dict[str, Any]:
    """Search official NexaBank knowledge base and customer FAQs."""
    results = search_faqs(db, query)
    return {
        "status": "success",
        "query": query,
        "match_count": len(results),
        "matches": [f.model_dump() for f in results]
    }

TOOL_MAPPING = {
    "get_account_balance": tool_get_account_balance,
    "get_accounts": tool_get_accounts,
    "get_transactions": tool_get_transactions,
    "calculate_spending_summary": tool_calculate_spending_summary,
    "get_product_rates": tool_get_product_rates,
    "check_mock_loan_eligibility": tool_check_mock_loan_eligibility,
    "search_banking_faq": tool_search_banking_faq,
}
