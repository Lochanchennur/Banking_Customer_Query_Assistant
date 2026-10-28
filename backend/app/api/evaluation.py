from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.customer import Customer
from app.schemas.evaluation import EvalSummary
from app.services.auth_service import get_current_customer
from app.evaluation.runner import run_evaluation_suite, latest_eval_cache

router = APIRouter(prefix="/evaluation", tags=["Evaluation & Diagnostics"])

@router.post("/run", response_model=EvalSummary)
def trigger_evaluation(
    current_user: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """Run the 55-question automated evaluation benchmark against the active banking engine."""
    return run_evaluation_suite(db=db, test_customer=current_user)

@router.get("/latest")
def get_latest_evaluation(
    current_user: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """Retrieve the most recent benchmark run or execute fresh if empty."""
    if latest_eval_cache:
        return latest_eval_cache
    return run_evaluation_suite(db=db, test_customer=current_user)
