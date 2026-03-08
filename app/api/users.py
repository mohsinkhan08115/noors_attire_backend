# api/users.py

from fastapi import APIRouter, HTTPException, Header
from typing import Optional
from app.services import auth_service
from app.services.firebase_service import db

router = APIRouter()


@router.get("/profile")
def get_profile(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = authorization.replace("Bearer ", "")
    user = auth_service.get_user_from_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    # Remove password hash before returning
    user.pop("password_hash", None)
    return user


@router.put("/profile")
def update_profile(
    update_data: dict,
    authorization: Optional[str] = Header(None)
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = authorization.replace("Bearer ", "")
    user = auth_service.get_user_from_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Only allow updating safe fields
    allowed = ["name", "phone"]
    safe_update = {k: v for k, v in update_data.items() if k in allowed}

    db.collection("users").document(user["id"]).update(safe_update)
    return {"message": "Profile updated", "updated_fields": list(safe_update.keys())}