from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.customer import Customer
from app.schemas.banking import DashboardSummaryResponse
from app.services.auth_service import get_current_customer
from app.services.banking_service import get_dashboard_summary

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("", response_model=DashboardSummaryResponse)
def get_dashboard(
    current_user: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    return get_dashboard_summary(db, customer_id=current_user.id, customer_name=current_user.name)
