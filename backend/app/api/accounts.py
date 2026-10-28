from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.customer import Customer
from app.schemas.banking import AccountSchema, AccountBalanceSchema
from app.services.auth_service import get_current_customer
from app.services.banking_service import (
    get_customer_accounts,
    get_account_by_id,
    get_account_balance
)

router = APIRouter(prefix="/accounts", tags=["Accounts"])

@router.get("", response_model=List[AccountSchema])
def list_accounts(
    current_user: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    return get_customer_accounts(db, current_user.id)

@router.get("/{account_id}", response_model=AccountSchema)
def get_account(
    account_id: str,
    current_user: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    return get_account_by_id(db, account_id=account_id, customer_id=current_user.id)

@router.get("/{account_id}/balance", response_model=AccountBalanceSchema)
def get_balance(
    account_id: str,
    current_user: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    return get_account_balance(db, account_id=account_id, customer_id=current_user.id)
