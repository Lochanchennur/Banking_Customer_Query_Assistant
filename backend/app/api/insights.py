from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.customer import Customer
from app.schemas.banking import SpendingInsightsResponse
from app.services.auth_service import get_current_customer
from app.services.banking_service import calculate_spending_insights

router = APIRouter(prefix="/insights", tags=["Insights"])

@router.get("/spending", response_model=SpendingInsightsResponse)
def get_spending_insights(
    period: str = Query("last_month", description="'this_month', 'last_month', or 'all'"),
    current_user: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    return calculate_spending_insights(db, customer_id=current_user.id, period=period)
