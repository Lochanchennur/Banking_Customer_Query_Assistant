from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.banking import BankingProductSchema
from app.services.banking_service import get_banking_products

router = APIRouter(prefix="/products", tags=["Banking Products"])

@router.get("", response_model=List[BankingProductSchema])
def list_products(
    product_type: Optional[str] = Query(None, description="PERSONAL_LOAN, HOME_LOAN, FIXED_DEPOSIT, SAVINGS_ACCOUNT"),
    db: Session = Depends(get_db)
):
    return get_banking_products(db, product_type=product_type)

@router.get("/rates")
def list_product_rates(db: Session = Depends(get_db)):
    products = get_banking_products(db)
    return {
        "as_of": "Current Demo Cycle",
        "benchmark_repo_rate": "6.50%",
        "rates": [
            {
                "product_id": p.id,
                "name": p.name,
                "type": p.product_type,
                "interest_rate": f"{p.interest_rate}% p.a.",
                "rate_type": p.rate_type,
                "range": f"₹{p.min_amount:,.0f} - ₹{p.max_amount:,.0f}",
                "tenure": f"{p.min_tenure_months} to {p.max_tenure_months} months"
            }
            for p in products
        ]
    }
