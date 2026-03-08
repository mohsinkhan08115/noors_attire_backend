# app/services/auth_service.py

from datetime import datetime
from typing import Optional
from app.services.firebase_service import get_all, get_one, create_one, query_by_field
from app.core.security import hash_password, verify_password, create_access_token
from app.schemas.user_schema import SignupRequest, LoginRequest

COLLECTION = "users"


def signup(data: SignupRequest) -> Optional[dict]:
    # Check if email already exists
    existing = query_by_field(COLLECTION, "email", data.email)
    if existing:
        return None

    user_data = {
        "name": data.name,
        "email": data.email,
        "password_hash": hash_password(data.password),
        "phone": data.phone,
        "role": "customer",
        "created_at": datetime.utcnow().isoformat(),
    }

    created = create_one(COLLECTION, user_data)
    user_id = created["id"]

    token = create_access_token({"sub": user_id, "email": data.email})

    return {
        "user": {
            "id": user_id,
            "name": user_data["name"],
            "email": user_data["email"],
            "phone": user_data["phone"],
            "created_at": user_data["created_at"],
        },
        "access_token": token,
        "token_type": "bearer"
    }


def login(data: LoginRequest) -> Optional[dict]:
    users = query_by_field(COLLECTION, "email", data.email)
    if not users:
        return None

    user = users[0]

    if not verify_password(data.password, user.get("password_hash", "")):
        return None

    token = create_access_token({"sub": user["id"], "email": user["email"]})

    return {
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "phone": user.get("phone"),
            "created_at": user.get("created_at"),
        },
        "access_token": token,
        "token_type": "bearer"
    }


def get_user_from_token(token: str) -> Optional[dict]:
    from app.core.security import decode_access_token
    payload = decode_access_token(token)
    if not payload:
        return None

    user_id = payload.get("sub")
    if not user_id:
        return None

    return get_one(COLLECTION, user_id)