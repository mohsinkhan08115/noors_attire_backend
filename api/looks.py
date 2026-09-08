# api/looks.py

from fastapi import APIRouter, HTTPException, Header, Query
from typing import Optional, List
from app.schemas.look_schema import LookCreate, LookUpdate, LookResponse
from app.services import look_service, auth_service

router = APIRouter()


def _require_admin(authorization: Optional[str]) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authentication required")
    token = authorization.replace("Bearer ", "")
    user = auth_service.get_user_from_token(token)
    if not user or user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


@router.get("/", response_model=List[LookResponse])
def get_looks(status: Optional[str] = Query("active", description="Filter by status")):
    """Get all outfit looks for the Build Your Own Look feature."""
    return look_service.get_all_looks(status=status)


@router.get("/{look_id}", response_model=LookResponse)
def get_look(look_id: str):
    """Get single look details."""
    look = look_service.get_look_by_id(look_id)
    if not look:
        raise HTTPException(status_code=404, detail="Look not found")
    return look


@router.post("/", response_model=LookResponse, status_code=201)
def create_look(look: LookCreate, authorization: Optional[str] = Header(None)):
    """Admin: Create a new predefined look bundle."""
    _require_admin(authorization)
    return look_service.create_look(look)


@router.put("/{look_id}", response_model=LookResponse)
def update_look(
    look_id: str,
    look: LookUpdate,
    authorization: Optional[str] = Header(None)
):
    """Admin: Update an existing look."""
    _require_admin(authorization)
    updated = look_service.update_look(look_id, look)
    if not updated:
        raise HTTPException(status_code=404, detail="Look not found")
    return updated


@router.delete("/{look_id}")
def delete_look(look_id: str, authorization: Optional[str] = Header(None)):
    """Admin: Delete a look."""
    _require_admin(authorization)
    success = look_service.delete_look(look_id)
    if not success:
        raise HTTPException(status_code=404, detail="Look not found")
    return {"message": "Look deleted successfully"}
