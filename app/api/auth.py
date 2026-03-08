# api/auth.py
#
# Authentication endpoints.
# POST /auth/signup → create account
# POST /auth/login  → get JWT token
# GET  /auth/me     → get current user (requires token)

from fastapi import APIRouter, HTTPException, Header
from typing import Optional
from app.schemas.user_schema import SignupRequest, LoginRequest, AuthResponse, UserResponse
from app.services import auth_service

router = APIRouter()


@router.post("/signup", response_model=AuthResponse, status_code=201)
def signup(data: SignupRequest):
    """
    Register a new user account.
    
    Request body:
    {
      "name": "Noor Ahmed",
      "email": "noor@example.com",
      "password": "mypassword123",
      "phone": "+92300000000"
    }
    
    Response:
    {
      "user": { "id": "...", "name": "Noor Ahmed", ... },
      "access_token": "eyJ...",
      "token_type": "bearer"
    }
    
    Save the access_token in Flutter — send it with every protected request.
    """
    result = auth_service.signup(data)
    if not result:
        raise HTTPException(
            status_code=400,
            detail="Email already registered. Please log in instead."
        )
    return result


@router.post("/login", response_model=AuthResponse)
def login(data: LoginRequest):
    """
    Log in with email and password.
    Returns a JWT token valid for 7 days.
    
    Request body:
    {
      "email": "noor@example.com",
      "password": "mypassword123"
    }
    """
    result = auth_service.login(data)
    if not result:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )
    return result


@router.get("/me", response_model=UserResponse)
def get_current_user(authorization: Optional[str] = Header(None)):
    """
    Get the currently logged-in user's profile.
    
    Requires Authorization header: "Bearer <your_token>"
    
    In Flutter:
      headers: {'Authorization': 'Bearer $token'}
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")

    token = authorization.replace("Bearer ", "")
    user = auth_service.get_user_from_token(token)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return user