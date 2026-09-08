# api/variants.py

from fastapi import APIRouter, HTTPException, Header, Body
from typing import Optional, List
from app.schemas.variant_schema import VariantCreate, VariantUpdate, VariantResponse
from app.services import variant_service, auth_service

router = APIRouter()


def _require_admin(authorization: Optional[str]) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authentication required")
    token = authorization.replace("Bearer ", "")
    user = auth_service.get_user_from_token(token)
    if not user or user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


@router.get("/{product_id}/variants", response_model=List[VariantResponse])
def get_variants(product_id: str):
    """Get all size/color variants for a product."""
    return variant_service.get_product_variants(product_id)


@router.post("/{product_id}/variants", response_model=VariantResponse, status_code=201)
def create_variant(
    product_id: str,
    variant: VariantCreate,
    authorization: Optional[str] = Header(None)
):
    """Admin: Add a new size/color variant to a product."""
    _require_admin(authorization)
    try:
        return variant_service.add_product_variant(product_id, variant)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{product_id}/variants/{variant_id}", response_model=VariantResponse)
def update_variant(
    product_id: str,
    variant_id: str,
    update_data: VariantUpdate,
    authorization: Optional[str] = Header(None)
):
    """Admin: Update variant details."""
    _require_admin(authorization)
    updated = variant_service.update_product_variant(product_id, variant_id, update_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Variant not found")
    return updated


@router.put("/{product_id}/variants/{variant_id}/stock")
def update_variant_stock(
    product_id: str,
    variant_id: str,
    data: dict = Body(...),
    authorization: Optional[str] = Header(None)
):
    """Admin: Update stock level for a variant."""
    _require_admin(authorization)
    stock = data.get("stock")
    if stock is None or stock < 0:
        raise HTTPException(status_code=400, detail="Stock count must be a non-negative integer")

    update_dto = VariantUpdate(stock=stock)
    updated = variant_service.update_product_variant(product_id, variant_id, update_dto)
    if not updated:
        raise HTTPException(status_code=404, detail="Variant not found")
    return {"message": "Stock updated successfully", "variant": updated}


@router.delete("/{product_id}/variants/{variant_id}")
def delete_variant(
    product_id: str,
    variant_id: str,
    authorization: Optional[str] = Header(None)
):
    """Admin: Delete a variant."""
    _require_admin(authorization)
    success = variant_service.delete_product_variant(product_id, variant_id)
    if not success:
        raise HTTPException(status_code=404, detail="Variant not found")
    return {"message": "Variant deleted successfully"}
