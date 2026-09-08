# app/services/alert_service.py

from typing import List, Dict, Any
from datetime import datetime
from app.services.firebase_service import get_all, create_one, delete_one, query_by_field

def create_stock_alert(email: str, product_id: str, variant_id: str | None = None, user_id: str | None = None) -> Dict[str, Any]:
    # Prevent duplicate active subscriptions
    existing = get_all("stock_alerts")
    for a in existing:
        if a.get("email") == email and a.get("product_id") == product_id and a.get("status") == "active":
            return a

    alert_data = {
        "user_id": user_id,
        "email": email,
        "product_id": product_id,
        "variant_id": variant_id,
        "alert_type": "back_in_stock",
        "status": "active",
        "created_at": datetime.utcnow().isoformat()
    }
    return create_one("stock_alerts", alert_data)


def create_price_alert(email: str, product_id: str, target_price: float | None = None, user_id: str | None = None) -> Dict[str, Any]:
    existing = get_all("price_alerts")
    for a in existing:
        if a.get("email") == email and a.get("product_id") == product_id and a.get("status") == "active":
            return a

    alert_data = {
        "user_id": user_id,
        "email": email,
        "product_id": product_id,
        "target_price": target_price,
        "alert_type": "price_drop",
        "status": "active",
        "created_at": datetime.utcnow().isoformat()
    }
    return create_one("price_alerts", alert_data)


def trigger_stock_replenishment_notifications(product_id: str, new_stock: int) -> List[Dict[str, Any]]:
    """
    Called when product/variant stock is replenished (> 0).
    Identifies matching subscribers and triggers notification event.
    """
    if new_stock <= 0:
        return []

    alerts = query_by_field("stock_alerts", "product_id", product_id)
    triggered = []
    for a in alerts:
        if a.get("status") == "active":
            # Simulate trigger/email log
            a["status"] = "triggered"
            a["triggered_at"] = datetime.utcnow().isoformat()
            triggered.append(a)
    return triggered
