from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.customer import Customer
from app.schemas.banking import TransactionListResponse
from app.services.auth_service import get_current_customer
from app.services.banking_service import get_customer_transactions

router = APIRouter(prefix="/transactions", tags=["Transactions"])

@router.get("", response_model=TransactionListResponse)
def list_transactions(
    account_id: Optional[str] = Query(None, description="Filter by specific account ID"),
    category: Optional[str] = Query(None, description="Filter by category (e.g. DINING, GROCERIES, UTILITIES)"),
    direction: Optional[str] = Query(None, description="DEBIT or CREDIT"),
    search: Optional[str] = Query(None, description="Search merchant or description"),
    start_date: Optional[datetime] = Query(None, description="Start date filter"),
    end_date: Optional[datetime] = Query(None, description="End date filter"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    return get_customer_transactions(
        db=db,
        customer_id=current_user.id,
        account_id=account_id,
        category=category,
        direction=direction,
        search=search,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset
    )

@router.get("/summary")
def get_transaction_summary(
    current_user: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    resp = get_customer_transactions(db=db, customer_id=current_user.id, limit=100)
    return {
        "customer_id": current_user.id,
        "total_count": resp.total_count,
        "total_debits": resp.total_debits,
        "total_credits": resp.total_credits,
        "net_flow": resp.total_credits - resp.total_debits
    }
