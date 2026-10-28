from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.customer import Customer
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.auth_service import get_current_customer
from app.ai.agent import execute_chat_query

router = APIRouter(prefix="/chat", tags=["AI Assistant"])

@router.post("", response_model=ChatResponse)
def chat_with_assistant(
    request: ChatRequest,
    current_user: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    return execute_chat_query(db=db, customer=current_user, request=request)
