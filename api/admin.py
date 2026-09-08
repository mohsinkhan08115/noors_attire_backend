# api/admin.py
#
# Admin-only endpoints. Every route is protected by _require_admin().
# Only users with role="admin" in Firebase can access these.
#
# Register in api/index.py:
#   from api.admin import router as admin_router
#   app.include_router(admin_router, prefix="/admin", tags=["Admin"])

from fastapi import APIRouter, HTTPException, Header, UploadFile, File, Request
from typing import Optional, List
from datetime import datetime
from app.services import auth_service, homepage_service
from app.services.firebase_service import get_all, get_one, create_one, update_one, delete_one
from app.schemas.homepage_schema import HomepageConfig

router = APIRouter()


# ─────────────────────────────────────────────────────────────────────────────
# AUTH GUARD
# ─────────────────────────────────────────────────────────────────────────────

def _require_admin(authorization: Optional[str]) -> dict:
    """
    Extract JWT token from Authorization header, verify it,
    and confirm the user has role='admin'.
    Raises 401 or 403 on failure.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authentication required")

    token = authorization.replace("Bearer ", "")
    user = auth_service.get_user_from_token(token)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    return user


# ─────────────────────────────────────────────────────────────────────────────
# DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/dashboard/stats")
def get_dashboard_stats(authorization: Optional[str] = Header(None)):
    """
    Returns aggregated stats for the admin dashboard overview.
    Includes revenue, order counts, low-stock alerts, top products, stock alert counts, and looks.
    """
    _require_admin(authorization)

    products     = get_all("products")
    orders       = get_all("orders")
    users        = get_all("users")
    looks        = get_all("looks")
    stock_alerts = get_all("stock_alerts")

    total_revenue    = sum(o.get("total_amount", 0) for o in orders if o.get("status") != "cancelled")
    pending_orders   = [o for o in orders if o.get("status") == "pending"]
    low_stock        = [p for p in products if int(p.get("stock", 0)) <= 3]
    recent_orders    = sorted(orders, key=lambda x: x.get("created_at", ""), reverse=True)[:10]

    # Calculate Top Products by order frequency
    product_sales_count = {}
    for o in orders:
        if o.get("status") != "cancelled":
            for item in o.get("items", []):
                p_name = item.get("product_name", "Unknown Item")
                product_sales_count[p_name] = product_sales_count.get(p_name, 0) + item.get("quantity", 1)

    top_products = sorted(
        [{"name": k, "sales": v} for k, v in product_sales_count.items()],
        key=lambda x: x["sales"],
        reverse=True
    )[:5]

    return {
        "total_revenue":               round(total_revenue, 2),
        "total_orders":                len(orders),
        "total_products":              len(products),
        "total_users":                 len(users),
        "total_looks":                 len(looks),
        "active_stock_subscriptions":  len([s for s in stock_alerts if s.get("status") == "active"]),
        "pending_orders":              len(pending_orders),
        "low_stock_products":          len(low_stock),
        "top_selling_products":        top_products,
        "recent_orders":               recent_orders,
    }


# ─────────────────────────────────────────────────────────────────────────────
# ORDERS
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/orders")
def get_all_orders(
    status: Optional[str] = None,
    authorization: Optional[str] = Header(None),
):
    """
    Get all orders, optionally filtered by status.
    Returns newest first.
    """
    _require_admin(authorization)

    orders = get_all("orders")

    if status:
        valid = ["pending", "confirmed", "shipped", "delivered", "cancelled"]
        if status not in valid:
            raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid}")
        orders = [o for o in orders if o.get("status") == status]

    return sorted(orders, key=lambda x: x.get("created_at", ""), reverse=True)


@router.put("/orders/{order_id}/status")
def update_order_status(
    order_id: str,
    payload: dict,
    authorization: Optional[str] = Header(None),
):
    """
    Update the status of a specific order.

    Request body:
      { "status": "confirmed" }

    Valid statuses: pending | confirmed | shipped | delivered | cancelled
    """
    _require_admin(authorization)

    new_status = payload.get("status")
    valid = ["pending", "confirmed", "shipped", "delivered", "cancelled"]

    if new_status not in valid:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid}")

    updated = update_one("orders", order_id, {
        "status":     new_status,
        "updated_at": datetime.utcnow().isoformat(),
    })

    if not updated:
        raise HTTPException(status_code=404, detail="Order not found")

    return {"message": f"Status updated to '{new_status}'", "order": updated}


# ─────────────────────────────────────────────────────────────────────────────
# USERS
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/users")
def get_all_users(authorization: Optional[str] = Header(None)):
    """
    Get all registered users.
    Password hashes are stripped before returning.
    """
    _require_admin(authorization)

    users = get_all("users")
    for u in users:
        u.pop("password_hash", None)  # Never expose hashed passwords

    return sorted(users, key=lambda x: x.get("created_at", ""), reverse=True)


@router.put("/users/{user_id}/role")
def update_user_role(
    user_id: str,
    payload: dict,
    authorization: Optional[str] = Header(None),
):
    """
    Change a user's role.

    Request body:
      { "role": "admin" }   or   { "role": "customer" }
    """
    _require_admin(authorization)

    new_role = payload.get("role")
    if new_role not in ["admin", "customer"]:
        raise HTTPException(status_code=400, detail="Role must be 'admin' or 'customer'")

    updated = update_one("users", user_id, {
        "role":       new_role,
        "updated_at": datetime.utcnow().isoformat(),
    })

    if not updated:
        raise HTTPException(status_code=404, detail="User not found")

    return {"message": f"Role updated to '{new_role}'"}


@router.put("/users/{user_id}/block")
def toggle_user_block(
    user_id: str,
    payload: dict,
    authorization: Optional[str] = Header(None),
):
    """
    Block or unblock a user account.

    Request body:
      { "blocked": true }   or   { "blocked": false }
    """
    _require_admin(authorization)

    blocked = payload.get("blocked", True)

    updated = update_one("users", user_id, {
        "blocked":    blocked,
        "updated_at": datetime.utcnow().isoformat(),
    })

    if not updated:
        raise HTTPException(status_code=404, detail="User not found")

    return {"message": f"User {'blocked' if blocked else 'unblocked'} successfully"}


# ─────────────────────────────────────────────────────────────────────────────
# STORE SETTINGS
# ─────────────────────────────────────────────────────────────────────────────

ALLOWED_SETTING_KEYS = {
    "store_name", "tagline", "contact_email", "contact_phone",
    "address", "currency", "free_shipping_threshold",
    "maintenance_mode", "meta_title", "default_order_status",
}


@router.get("/settings")
def get_store_settings(authorization: Optional[str] = Header(None)):
    """Get store settings from Firebase Realtime Database."""
    _require_admin(authorization)

    settings = get_one("settings", "store")
    return settings or {}


@router.put("/settings")
def update_store_settings(
    payload: dict,
    authorization: Optional[str] = Header(None),
):
    """
    Update store settings in Firebase.
    Only whitelisted keys are accepted (prevents overwriting sensitive fields).
    """
    _require_admin(authorization)

    safe = {k: v for k, v in payload.items() if k in ALLOWED_SETTING_KEYS}
    safe["updated_at"] = datetime.utcnow().isoformat()

    # Write directly to Firebase Realtime Database
    import firebase_admin
    from firebase_admin import db
    db.reference("settings/store").update(safe)

    return {"message": "Settings updated successfully", "updated_fields": list(safe.keys())}


# ─────────────────────────────────────────────────────────────────────────────
# HOMEPAGE CMS
# ─────────────────────────────────────────────────────────────────────────────

@router.put("/homepage")
def update_homepage(
    config: HomepageConfig,
    authorization: Optional[str] = Header(None),
):
    """
    Replace the homepage configuration: announcement bar, hero content,
    and section enable/order. See GET /homepage for the public read side.
    """
    _require_admin(authorization)
    return homepage_service.update_homepage(config)


@router.post("/homepage/upload-image")
def upload_homepage_image(
    request: Request,
    file: UploadFile = File(...),
    authorization: Optional[str] = Header(None)
):
    """
    Upload a new website picture (hero image) to local storage and return the URL.
    """
    _require_admin(authorization)

    content = file.file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file")

    filename = f"homepage/hero_{int(datetime.utcnow().timestamp())}_{file.filename}"
    from app.services.local_storage_service import save_local_image
    
    try:
        public_url = save_local_image(content, filename, request)
        return {"image_url": public_url, "message": "Image uploaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Upload failed: {str(e)}")