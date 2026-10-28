from typing import Optional, List
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.security import (
    verify_password,
    create_access_token,
    decode_access_token,
    security_scheme,
)
from app.database.session import get_db
from app.models.customer import Customer
from app.schemas.auth import LoginRequest, TokenResponse, CustomerPublic
from app.core.config import settings

def authenticate_customer(db: Session, email: str, password: str) -> Optional[Customer]:
    customer = db.query(Customer).filter(Customer.email == email.lower().strip()).first()
    if not customer:
        return None
    if not verify_password(password, customer.hashed_password):
        return None
    return customer

def get_current_customer(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    db: Session = Depends(get_db)
) -> Customer:
    """Validate bearer token and return current authenticated customer."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token is missing. Please log in.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    payload = decode_access_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session has expired or is invalid. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    customer_id = payload.get("sub")
    if not customer_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials payload.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authenticated customer account not found.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return customer

def list_demo_customers(db: Session) -> List[CustomerPublic]:
    """Helper for demo switcher UI to easily demonstrate multi-customer isolation."""
    customers = db.query(Customer).all()
    return [
        CustomerPublic(
            id=c.id,
            name=c.name,
            email=c.email,
            phone=c.phone,
            occupation=c.occupation,
            monthly_income=c.monthly_income,
            credit_score=c.credit_score,
            avatar_url=c.avatar_url
        )
        for c in customers
    ]
