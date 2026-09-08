# api/alerts.py

from fastapi import APIRouter, HTTPException, Header
from typing import Optional
from app.schemas.alert_schema import StockAlertCreate, PriceAlertCreate, AlertResponse
from app.services import alert_service, auth_service
from app.services.firebase_service import delete_one, get_one

router = APIRouter()


def _get_optional_user(authorization: Optional[str]) -> Optional[dict]:
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.replace("Bearer ", "")
    return auth_service.get_user_from_token(token)


@router.post("/back-in-stock", response_model=AlertResponse, status_code=201)
def subscribe_back_in_stock(data: StockAlertCreate, authorization: Optional[str] = Header(None)):
    """Register email alert when out-of-stock item is replenished."""
    user = _get_optional_user(authorization)
    user_id = user["id"] if user else None
    return alert_service.create_stock_alert(
        email=data.email,
        product_id=data.product_id,
        variant_id=data.variant_id,
        user_id=user_id
    )


@router.post("/price-drop", response_model=AlertResponse, status_code=201)
def subscribe_price_drop(data: PriceAlertCreate, authorization: Optional[str] = Header(None)):
    """Register email alert when price drops on a dress or shirt."""
    user = _get_optional_user(authorization)
    user_id = user["id"] if user else None
    return alert_service.create_price_alert(
        email=data.email,
        product_id=data.product_id,
        target_price=data.target_price,
        user_id=user_id
    )


@router.delete("/back-in-stock/{alert_id}")
def cancel_stock_alert(alert_id: str):
    """Unsubscribe from stock alert."""
    success = delete_one("stock_alerts", alert_id)
    if not success:
        raise HTTPException(status_code=404, detail="Alert subscription not found")
    return {"message": "Unsubscribed from stock alert"}


@router.delete("/price-drop/{alert_id}")
def cancel_price_alert(alert_id: str):
    """Unsubscribe from price drop alert."""
    success = delete_one("price_alerts", alert_id)
    if not success:
        raise HTTPException(status_code=404, detail="Alert subscription not found")
    return {"message": "Unsubscribed from price drop alert"}
