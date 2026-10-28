from datetime import datetime
from typing import List, Optional, Dict
from pydantic import BaseModel, Field

class AccountSchema(BaseModel):
    id: str
    customer_id: str
    account_number_masked: str
    account_type: str
    account_name: str
    currency: str
    balance: float
    available_balance: float
    status: str
    interest_rate: float
    created_at: datetime

class AccountBalanceSchema(BaseModel):
    account_id: str
    account_name: str
    account_number_masked: str
    currency: str
    balance: float
    available_balance: float
    as_of: datetime

class TransactionSchema(BaseModel):
    id: str
    account_id: str
    customer_id: str
    timestamp: datetime
    merchant_or_description: str
    category: str
    amount: float
    direction: str
    status: str
    reference_number: Optional[str] = None
    account_masked: Optional[str] = None

class TransactionFilterParams(BaseModel):
    account_id: Optional[str] = None
    category: Optional[str] = None
    direction: Optional[str] = None
    search: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: int = 50
    offset: int = 0

class TransactionListResponse(BaseModel):
    total_count: int
    items: List[TransactionSchema]
    total_debits: float
    total_credits: float

class CategorySpending(BaseModel):
    category: str
    amount: float
    percentage: float
    transaction_count: int

class MonthlyTrend(BaseModel):
    month: str  # YYYY-MM
    income: float
    expense: float
    net: float

class SpendingInsightsResponse(BaseModel):
    period: str
    total_spent: float
    total_income: float
    net_savings: float
    by_category: List[CategorySpending]
    monthly_trends: List[MonthlyTrend]
    largest_expenses: List[TransactionSchema]

class DashboardSummaryResponse(BaseModel):
    customer_name: str
    total_balance: float
    total_available_balance: float
    total_accounts: int
    total_debits_period: float
    recent_transaction_count: int
    accounts: List[AccountSchema]
    recent_transactions: List[TransactionSchema]
    category_spending: List[CategorySpending]
    monthly_trends: List[MonthlyTrend]

class BankingProductSchema(BaseModel):
    id: str
    product_type: str
    name: str
    headline: str
    interest_rate: float
    rate_type: str
    min_amount: float
    max_amount: float
    min_tenure_months: int
    max_tenure_months: int
    processing_fee_pct: float
    eligibility_criteria_summary: str
    min_income_monthly: float
    min_credit_score: int

class LoanEligibilityRequest(BaseModel):
    product_type: str = "PERSONAL_LOAN"  # PERSONAL_LOAN, HOME_LOAN
    requested_amount: float = Field(..., gt=0)
    tenure_months: int = Field(..., gt=0)
    declared_monthly_income: Optional[float] = None
    declared_existing_emis: Optional[float] = 0.0

class LoanEligibilityResponse(BaseModel):
    eligible: bool
    status: str  # APPROVED, REJECTED, CONDITIONAL
    product_type: str
    requested_amount: float
    approved_amount: float
    tenure_months: int
    interest_rate: float
    estimated_emi: float
    debt_to_income_ratio_pct: float
    reason: str
    criteria_evaluation: Dict[str, bool]
    disclaimer: str = "Illustrative demonstration calculation only. Not an actual credit decision or binding financial offer."

class FAQSchema(BaseModel):
    id: str
    category: str
    question: str
    answer: str
