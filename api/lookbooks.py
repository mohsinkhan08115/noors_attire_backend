# api/lookbooks.py

from fastapi import APIRouter, HTTPException, Header, Query
from typing import Optional, List
from app.schemas.lookbook_schema import LookbookCreate, LookbookUpdate, LookbookResponse, LookbookHotspot
from app.services import lookbook_service, auth_service

router = APIRouter()


def _require_admin(authorization: Optional[str]) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authentication required")
    token = authorization.replace("Bearer ", "")
    user = auth_service.get_user_from_token(token)
    if not user or user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


@router.get("/", response_model=List[LookbookResponse])
def get_lookbooks(status: Optional[str] = Query("active")):
    """Get public interactive lookbooks."""
    return lookbook_service.get_all_lookbooks(status=status)


@router.get("/{lookbook_id}", response_model=LookbookResponse)
def get_lookbook(lookbook_id: str):
    """Get single lookbook with hotspots."""
    lb = lookbook_service.get_lookbook_by_id(lookbook_id)
    if not lb:
        raise HTTPException(status_code=404, detail="Lookbook not found")
    return lb


@router.post("/", response_model=LookbookResponse, status_code=201)
def create_lookbook(data: LookbookCreate, authorization: Optional[str] = Header(None)):
    """Admin: Create new lookbook editorial."""
    _require_admin(authorization)
    return lookbook_service.create_lookbook(data)


@router.put("/{lookbook_id}", response_model=LookbookResponse)
def update_lookbook(
    lookbook_id: str,
    data: LookbookUpdate,
    authorization: Optional[str] = Header(None)
):
    """Admin: Update lookbook."""
    _require_admin(authorization)
    updated = lookbook_service.update_lookbook(lookbook_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Lookbook not found")
    return updated


@router.delete("/{lookbook_id}")
def delete_lookbook(lookbook_id: str, authorization: Optional[str] = Header(None)):
    """Admin: Delete lookbook."""
    _require_admin(authorization)
    success = lookbook_service.delete_lookbook(lookbook_id)
    if not success:
        raise HTTPException(status_code=404, detail="Lookbook not found")
    return {"message": "Lookbook deleted successfully"}


@router.post("/{lookbook_id}/hotspots")
def add_hotspot(
    lookbook_id: str,
    hotspot: LookbookHotspot,
    authorization: Optional[str] = Header(None)
):
    """Admin: Add product pin hotspot to lookbook photo."""
    _require_admin(authorization)
    hs = lookbook_service.add_hotspot(lookbook_id, hotspot)
    if not hs:
        raise HTTPException(status_code=404, detail="Lookbook not found")
    return {"message": "Hotspot added successfully", "hotspot": hs}


@router.delete("/{lookbook_id}/hotspots/{hotspot_id}")
def delete_hotspot(
    lookbook_id: str,
    hotspot_id: str,
    authorization: Optional[str] = Header(None)
):
    """Admin: Remove hotspot pin."""
    _require_admin(authorization)
    success = lookbook_service.remove_hotspot(lookbook_id, hotspot_id)
    if not success:
        raise HTTPException(status_code=404, detail="Hotspot not found")
    return {"message": "Hotspot removed successfully"}
