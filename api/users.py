# api/users.py

from fastapi import APIRouter, HTTPException, Header, Body
from typing import Optional
from datetime import datetime
from app.services import auth_service
from app.services.firebase_service import create_one, get_one, update_one

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

    updated = update_one("users", user["id"], safe_update)
    return {"message": "Profile updated", "updated_fields": list(safe_update.keys())}


@router.post("/subscribe")
def subscribe_newsletter(data: dict = Body(...)):
    email = data.get("email", "").strip().lower()
    if not email or "@" not in email:
        raise HTTPException(status_code=400, detail="Please enter a valid email address")

    sub_data = {
        "email": email,
        "subscribed_at": datetime.utcnow().isoformat(),
        "status": "active"
    }
    created = create_one("subscribers", sub_data)
    return {"message": "Thank you for subscribing to Noor's Attire!", "subscription": created}


# ── Recently Viewed Endpoints ────────────────────────────────────────────────

def _get_authenticated_user(authorization: Optional[str]):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = authorization.replace("Bearer ", "")
    user = auth_service.get_user_from_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user


@router.get("/me/recently-viewed")
def get_recently_viewed(authorization: Optional[str] = Header(None)):
    """Get authenticated user's recently viewed products history."""
    user = _get_authenticated_user(authorization)
    from app.services.firebase_service import set_one
    doc = get_one("recently_viewed", user["id"])
    if not doc:
        return []
    return doc.get("items", [])


@router.post("/me/recently-viewed")
def add_recently_viewed(data: dict = Body(...), authorization: Optional[str] = Header(None)):
    """Record a viewed product ID for authenticated user."""
    user = _get_authenticated_user(authorization)
    product_id = data.get("product_id")
    if not product_id:
        raise HTTPException(status_code=400, detail="product_id is required")

    from app.services.firebase_service import set_one
    doc = get_one("recently_viewed", user["id"]) or {"items": []}
    items = doc.get("items", [])

    # Remove existing to place newest at top
    items = [i for i in items if i.get("product_id") != product_id]
    items.insert(0, {
        "product_id": product_id,
        "viewed_at": datetime.utcnow().isoformat()
    })

    # Keep maximum 20 items per user
    if len(items) > 20:
        items = items[:20]

    set_one("recently_viewed", user["id"], {"items": items})
    return {"message": "Viewed product recorded", "count": len(items)}


@router.delete("/me/recently-viewed")
def clear_recently_viewed(authorization: Optional[str] = Header(None)):
    """Clear recently viewed history."""
    user = _get_authenticated_user(authorization)
    from app.services.firebase_service import set_one
    set_one("recently_viewed", user["id"], {"items": []})
    return {"message": "History cleared"}