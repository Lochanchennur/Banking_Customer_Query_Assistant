from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.customer import Customer
from app.models.product import BankingProduct
from app.schemas.banking import LoanEligibilityRequest, LoanEligibilityResponse
from app.services.auth_service import get_current_customer
from app.services.loan_calculator import evaluate_loan_eligibility

router = APIRouter(prefix="/loans", tags=["Loans & Eligibility"])

@router.post("/eligibility", response_model=LoanEligibilityResponse)
def check_loan_eligibility(
    request: LoanEligibilityRequest,
    current_user: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    product = db.query(BankingProduct).filter(
        BankingProduct.product_type == request.product_type.upper().strip()
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Loan product '{request.product_type}' not found."
        )

    return evaluate_loan_eligibility(
        customer=current_user,
        product=product,
        requested_amount=request.requested_amount,
        tenure_months=request.tenure_months,
        declared_monthly_income=request.declared_monthly_income,
        declared_existing_emis=request.declared_existing_emis or 0.0
    )
