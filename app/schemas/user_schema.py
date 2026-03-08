# app/schemas/user_schema.py

from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class SignupRequest(BaseModel):
    """Data required to create a new account."""
    name: str = Field(..., min_length=2, max_length=50)
    email: EmailStr                                   # Auto-validates email format
    password: str = Field(..., min_length=6)
    phone: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Noor Ahmed",
                "email": "noor@example.com",
                "password": "securepass123",
                "phone": "+92300000000"
            }
        }


class LoginRequest(BaseModel):
    """Data required to log in."""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """User data returned after signup/login."""
    id: str
    name: str
    email: str
    phone: Optional[str] = None
    created_at: Optional[str] = None


class AuthResponse(BaseModel):
    """Full auth response: user info + JWT token."""
    user: UserResponse
    access_token: str
    token_type: str = "bearer"