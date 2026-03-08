# app/services/auth_service.py
#
# Handles user registration and login.
# Users are stored in Firestore (our database).
# Passwords are hashed with bcrypt before saving.
# On login, we return a JWT token.

from datetime import datetime
from typing import Optional
from app.services.firebase_service import db
from app.core.security import hash_password, verify_password, create_access_token
from app.schemas.user_schema import SignupRequest, LoginRequest


COLLECTION = "users"


def signup(data: SignupRequest) -> Optional[dict]:
    """
    Create a new user account.
    
    Steps:
    1. Check if email already exists
    2. Hash the password
    3. Save user to Firestore
    4. Return user data + JWT token
    """
    # Check if email already registered
    existing = (
        db.collection(COLLECTION)
        .where("email", "==", data.email)
        .limit(1)
        .get()
    )
    if existing:
        return None  # Email taken

    user_data = {
        "name": data.name,
        "email": data.email,
        "password_hash": hash_password(data.password),  # NEVER store plain text
        "phone": data.phone,
        "role": "customer",
        "created_at": datetime.utcnow().isoformat(),
    }

    _, doc_ref = db.collection(COLLECTION).add(user_data)
    user_data["id"] = doc_ref.id

    # Create JWT token
    token = create_access_token({"sub": doc_ref.id, "email": data.email})

    return {
        "user": {
            "id": doc_ref.id,
            "name": user_data["name"],
            "email": user_data["email"],
            "phone": user_data["phone"],
            "created_at": user_data["created_at"],
        },
        "access_token": token,
        "token_type": "bearer"
    }


def login(data: LoginRequest) -> Optional[dict]:
    """
    Authenticate a user.
    
    Steps:
    1. Find user by email in Firestore
    2. Verify password against stored hash
    3. Return user data + new JWT token
    """
    docs = (
        db.collection(COLLECTION)
        .where("email", "==", data.email)
        .limit(1)
        .get()
    )

    if not docs:
        return None  # User not found

    doc = docs[0]
    user = doc.to_dict()
    user["id"] = doc.id

    # Check password
    if not verify_password(data.password, user.get("password_hash", "")):
        return None  # Wrong password

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
    """
    Validate a JWT token and return the user.
    Used as a dependency in protected routes.
    """
    from app.core.security import decode_access_token
    payload = decode_access_token(token)
    if not payload:
        return None

    user_id = payload.get("sub")
    if not user_id:
        return None

    doc = db.collection(COLLECTION).document(user_id).get()
    if not doc.exists:
        return None

    user = doc.to_dict()
    user["id"] = doc.id
    return user