from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any, Tuple
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_, desc

from app.models.account import Account
from app.models.transaction import Transaction
from app.models.product import BankingProduct
from app.models.faq import FAQ
from app.schemas.banking import (
    AccountSchema,
    AccountBalanceSchema,
    TransactionSchema,
    TransactionListResponse,
    CategorySpending,
    MonthlyTrend,
    SpendingInsightsResponse,
    DashboardSummaryResponse,
    BankingProductSchema,
    FAQSchema
)

CATEGORY_ALIASES = {
    "food": ["DINING", "GROCERIES"],
    "dining": ["DINING"],
    "restaurants": ["DINING"],
    "restaurant": ["DINING"],
    "groceries": ["GROCERIES"],
    "grocery": ["GROCERIES"],
    "supermarket": ["GROCERIES"],
    "utility": ["UTILITIES"],
    "utilities": ["UTILITIES"],
    "bills": ["UTILITIES"],
    "electricity": ["UTILITIES"],
    "internet": ["UTILITIES"],
    "shopping": ["SHOPPING"],
    "clothes": ["SHOPPING"],
    "electronics": ["SHOPPING"],
    "travel": ["TRAVEL"],
    "flights": ["TRAVEL"],
    "transport": ["TRAVEL"],
    "cab": ["TRAVEL"],
    "uber": ["TRAVEL"],
    "entertainment": ["ENTERTAINMENT"],
    "movies": ["ENTERTAINMENT"],
    "health": ["HEALTHCARE"],
    "healthcare": ["HEALTHCARE"],
    "medical": ["HEALTHCARE"],
    "investments": ["INVESTMENTS"],
    "salary": ["SALARY"]
}

def verify_account_ownership(db: Session, account_id: str, customer_id: str) -> Account:
    """
    Enforce strict cross-customer account isolation.
    If the account exists but belongs to someone else, raise 403 Forbidden.
    """
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Account with ID '{account_id}' not found."
        )
    if account.customer_id != customer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: You do not have permission to view or access this account."
        )
    return account

def get_customer_accounts(db: Session, customer_id: str) -> List[AccountSchema]:
    accounts = db.query(Account).filter(Account.customer_id == customer_id).all()
    return [
        AccountSchema(
            id=a.id,
            customer_id=a.customer_id,
            account_number_masked=a.account_number_masked,
            account_type=a.account_type,
            account_name=a.account_name,
            currency=a.currency,
            balance=a.balance,
            available_balance=a.available_balance,
            status=a.status,
            interest_rate=a.interest_rate,
            created_at=a.created_at
        )
        for a in accounts
    ]

def get_account_by_id(db: Session, account_id: str, customer_id: str) -> AccountSchema:
    account = verify_account_ownership(db, account_id, customer_id)
    return AccountSchema(
        id=account.id,
        customer_id=account.customer_id,
        account_number_masked=account.account_number_masked,
        account_type=account.account_type,
        account_name=account.account_name,
        currency=account.currency,
        balance=account.balance,
        available_balance=account.available_balance,
        status=account.status,
        interest_rate=account.interest_rate,
        created_at=account.created_at
    )

def get_account_balance(db: Session, account_id: str, customer_id: str) -> AccountBalanceSchema:
    account = verify_account_ownership(db, account_id, customer_id)
    return AccountBalanceSchema(
        account_id=account.id,
        account_name=account.account_name,
        account_number_masked=account.account_number_masked,
        currency=account.currency,
        balance=account.balance,
        available_balance=account.available_balance,
        as_of=datetime.now(timezone.utc)
    )

def get_total_balance(db: Session, customer_id: str) -> Dict[str, Any]:
    accounts = db.query(Account).filter(Account.customer_id == customer_id).all()
    total_bal = sum(a.balance for a in accounts)
    total_avail = sum(a.available_balance for a in accounts)
    return {
        "customer_id": customer_id,
        "total_balance": total_bal,
        "total_available_balance": total_avail,
        "currency": "INR",
        "account_count": len(accounts),
        "accounts": [
            {
                "id": a.id,
                "name": a.account_name,
                "type": a.account_type,
                "masked": a.account_number_masked,
                "balance": a.balance,
                "available": a.available_balance
            }
            for a in accounts
        ]
    }

def get_customer_transactions(
    db: Session,
    customer_id: str,
    account_id: Optional[str] = None,
    category: Optional[str] = None,
    direction: Optional[str] = None,
    search: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 50,
    offset: int = 0
) -> TransactionListResponse:
    # Build query strictly filtered by authenticated customer_id
    query = db.query(Transaction, Account.account_number_masked)\
        .join(Account, Transaction.account_id == Account.id)\
        .filter(Transaction.customer_id == customer_id)

    if account_id:
        verify_account_ownership(db, account_id, customer_id)
        query = query.filter(Transaction.account_id == account_id)

    if category:
        cat_key = category.strip().lower()
        if cat_key in CATEGORY_ALIASES:
            matched_cats = CATEGORY_ALIASES[cat_key]
            query = query.filter(Transaction.category.in_(matched_cats))
        else:
            query = query.filter(func.upper(Transaction.category) == category.strip().upper())

    if direction:
        query = query.filter(Transaction.direction == direction.strip().upper())

    if search:
        s = f"%{search.strip().lower()}%"
        query = query.filter(
            or_(
                func.lower(Transaction.merchant_or_description).like(s),
                func.lower(Transaction.category).like(s)
            )
        )

    if start_date:
        query = query.filter(Transaction.timestamp >= start_date)
    if end_date:
        query = query.filter(Transaction.timestamp <= end_date)

    total_count = query.count()

    # Sum total debits and credits
    all_filtered = query.all()
    total_debits = sum(t[0].amount for t in all_filtered if t[0].direction == "DEBIT")
    total_credits = sum(t[0].amount for t in all_filtered if t[0].direction == "CREDIT")

    # Order by timestamp desc and paginate
    paginated = query.order_by(desc(Transaction.timestamp)).offset(offset).limit(limit).all()

    items = [
        TransactionSchema(
            id=t[0].id,
            account_id=t[0].account_id,
            customer_id=t[0].customer_id,
            timestamp=t[0].timestamp,
            merchant_or_description=t[0].merchant_or_description,
            category=t[0].category,
            amount=t[0].amount,
            direction=t[0].direction,
            status=t[0].status,
            reference_number=t[0].reference_number,
            account_masked=t[1]
        )
        for t in paginated
    ]

    return TransactionListResponse(
        total_count=total_count,
        items=items,
        total_debits=total_debits,
        total_credits=total_credits
    )

def calculate_spending_insights(
    db: Session,
    customer_id: str,
    period: str = "last_month"  # "this_month", "last_month", "all"
) -> SpendingInsightsResponse:
    now = datetime.now(timezone.utc)
    
    if period == "this_month":
        start_date = datetime(now.year, now.month, 1, tzinfo=timezone.utc)
        end_date = now
    elif period == "last_month":
        # First day of previous month
        first_current = datetime(now.year, now.month, 1, tzinfo=timezone.utc)
        last_prev = first_current - timedelta(days=1)
        start_date = datetime(last_prev.year, last_prev.month, 1, tzinfo=timezone.utc)
        end_date = first_current
    else:  # all / 90 days
        start_date = now - timedelta(days=90)
        end_date = now

    txns = db.query(Transaction)\
        .filter(
            Transaction.customer_id == customer_id,
            Transaction.timestamp >= start_date,
            Transaction.timestamp <= end_date
        )\
        .order_by(desc(Transaction.timestamp))\
        .all()

    debits = [t for t in txns if t.direction == "DEBIT"]
    credits = [t for t in txns if t.direction == "CREDIT"]

    total_spent = sum(t.amount for t in debits)
    total_income = sum(t.amount for t in credits)
    net_savings = total_income - total_spent

    # Group by category
    cat_totals: Dict[str, Dict[str, Any]] = {}
    for d in debits:
        c = d.category
        if c not in cat_totals:
            cat_totals[c] = {"amount": 0.0, "count": 0}
        cat_totals[c]["amount"] += d.amount
        cat_totals[c]["count"] += 1

    by_category = [
        CategorySpending(
            category=cat,
            amount=round(info["amount"], 2),
            percentage=round((info["amount"] / total_spent * 100.0), 1) if total_spent > 0 else 0.0,
            transaction_count=info["count"]
        )
        for cat, info in sorted(cat_totals.items(), key=lambda x: x[1]["amount"], reverse=True)
    ]

    # Calculate monthly trends across all available records for this user
    all_user_txns = db.query(Transaction)\
        .filter(Transaction.customer_id == customer_id)\
        .order_by(Transaction.timestamp.asc())\
        .all()
    
    monthly_agg: Dict[str, Dict[str, float]] = {}
    for t in all_user_txns:
        m_key = t.timestamp.strftime("%Y-%m")
        if m_key not in monthly_agg:
            monthly_agg[m_key] = {"income": 0.0, "expense": 0.0}
        if t.direction == "CREDIT":
            monthly_agg[m_key]["income"] += t.amount
        else:
            monthly_agg[m_key]["expense"] += t.amount

    monthly_trends = [
        MonthlyTrend(
            month=m,
            income=round(data["income"], 2),
            expense=round(data["expense"], 2),
            net=round(data["income"] - data["expense"], 2)
        )
        for m, data in sorted(monthly_agg.items())
    ]

    largest_expenses = [
        TransactionSchema(
            id=t.id,
            account_id=t.account_id,
            customer_id=t.customer_id,
            timestamp=t.timestamp,
            merchant_or_description=t.merchant_or_description,
            category=t.category,
            amount=t.amount,
            direction=t.direction,
            status=t.status,
            reference_number=t.reference_number
        )
        for t in sorted(debits, key=lambda x: x.amount, reverse=True)[:5]
    ]

    return SpendingInsightsResponse(
        period=period,
        total_spent=round(total_spent, 2),
        total_income=round(total_income, 2),
        net_savings=round(net_savings, 2),
        by_category=by_category,
        monthly_trends=monthly_trends,
        largest_expenses=largest_expenses
    )

def get_dashboard_summary(db: Session, customer_id: str, customer_name: str) -> DashboardSummaryResponse:
    accounts = get_customer_accounts(db, customer_id)
    total_balance = sum(a.balance for a in accounts)
    total_avail = sum(a.available_balance for a in accounts)

    # 30 day debits
    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
    recent_txns_resp = get_customer_transactions(db, customer_id=customer_id, limit=5)
    
    insights = calculate_spending_insights(db, customer_id=customer_id, period="this_month")

    return DashboardSummaryResponse(
        customer_name=customer_name,
        total_balance=round(total_balance, 2),
        total_available_balance=round(total_avail, 2),
        total_accounts=len(accounts),
        total_debits_period=insights.total_spent,
        recent_transaction_count=recent_txns_resp.total_count,
        accounts=accounts,
        recent_transactions=recent_txns_resp.items,
        category_spending=insights.by_category,
        monthly_trends=insights.monthly_trends
    )

def get_banking_products(db: Session, product_type: Optional[str] = None) -> List[BankingProductSchema]:
    query = db.query(BankingProduct)
    if product_type:
        query = query.filter(BankingProduct.product_type == product_type.upper().strip())
    products = query.all()
    return [
        BankingProductSchema(
            id=p.id,
            product_type=p.product_type,
            name=p.name,
            headline=p.headline,
            interest_rate=p.interest_rate,
            rate_type=p.rate_type,
            min_amount=p.min_amount,
            max_amount=p.max_amount,
            min_tenure_months=p.min_tenure_months,
            max_tenure_months=p.max_tenure_months,
            processing_fee_pct=p.processing_fee_pct,
            eligibility_criteria_summary=p.eligibility_criteria_summary,
            min_income_monthly=p.min_income_monthly,
            min_credit_score=p.min_credit_score
        )
        for p in products
    ]

def search_faqs(db: Session, query: str) -> List[FAQSchema]:
    terms = query.lower().strip().split()
    all_faqs = db.query(FAQ).all()
    results = []
    for f in all_faqs:
        haystack = f"{f.question.lower()} {f.answer.lower()} {f.category.lower()} {(f.keywords or '').lower()}"
        score = sum(1 for term in terms if term in haystack)
        if score > 0:
            results.append((score, f))
    
    # Sort by relevance score
    results.sort(key=lambda x: x[0], reverse=True)
    return [
        FAQSchema(
            id=f.id,
            category=f.category,
            question=f.question,
            answer=f.answer
        )
        for _, f in results[:5]
    ]
