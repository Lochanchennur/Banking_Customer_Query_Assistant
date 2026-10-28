from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.customer import Customer
from app.schemas.auth import LoginRequest, TokenResponse, CustomerPublic
from app.services.auth_service import authenticate_customer, get_current_customer, list_demo_customers
from app.core.security import create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    customer = authenticate_customer(db, request.email, request.password)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password. For demo accounts, use demo123 as password."
        )
    
    token = create_access_token(data={"sub": customer.id, "email": customer.email, "name": customer.name})
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=86400,
        customer=CustomerPublic(
            id=customer.id,
            name=customer.name,
            email=customer.email,
            phone=customer.phone,
            occupation=customer.occupation,
            monthly_income=customer.monthly_income,
            credit_score=customer.credit_score,
            avatar_url=customer.avatar_url
        )
    )

@router.post("/logout")
def logout(current_user: Customer = Depends(get_current_customer)):
    return {"message": "Logged out successfully from session.", "customer_id": current_user.id}

@router.get("/me", response_model=CustomerPublic)
def get_me(current_user: Customer = Depends(get_current_customer)):
    return CustomerPublic(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        phone=current_user.phone,
        occupation=current_user.occupation,
        monthly_income=current_user.monthly_income,
        credit_score=current_user.credit_score,
        avatar_url=current_user.avatar_url
    )

@router.get("/demo-customers", response_model=List[CustomerPublic])
def get_demo_customers(db: Session = Depends(get_db)):
    """Provides demo profiles for one-click switching during TCS Technology Day presentation."""
    return list_demo_customers(db)
