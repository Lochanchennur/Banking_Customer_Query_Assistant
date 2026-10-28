from typing import Optional
from pydantic import BaseModel

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    customer: "CustomerPublic"

class CustomerPublic(BaseModel):
    id: str
    name: str
    email: str
    phone: Optional[str] = None
    occupation: Optional[str] = None
    monthly_income: float
    credit_score: int
    avatar_url: Optional[str] = None

TokenResponse.model_rebuild()
