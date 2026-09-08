# api/style_gallery.py

from fastapi import APIRouter, HTTPException, Header, Query
from typing import Optional, List
from app.schemas.style_gallery_schema import StyleSubmissionCreate, StyleSubmissionResponse
from app.services import style_gallery_service, auth_service

router = APIRouter()


def _get_optional_user(authorization: Optional[str]) -> Optional[dict]:
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.replace("Bearer ", "")
    return auth_service.get_user_from_token(token)


def _require_admin(authorization: Optional[str]) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authentication required")
    token = authorization.replace("Bearer ", "")
    user = auth_service.get_user_from_token(token)
    if not user or user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


@router.post("/submissions", response_model=StyleSubmissionResponse, status_code=201)
def submit_style_photo(data: StyleSubmissionCreate, authorization: Optional[str] = Header(None)):
    """Customer: Submit photo to styled by community gallery."""
    user = _get_optional_user(authorization)
    user_id = user["id"] if user else None
    return style_gallery_service.submit_style_photo(user_id, data)


@router.get("/gallery", response_model=List[StyleSubmissionResponse])
def get_public_gallery():
    """Public: Get approved customer styled photos."""
    return style_gallery_service.get_public_style_gallery()


@router.get("/admin/submissions", response_model=List[StyleSubmissionResponse])
def get_all_submissions(
    status: Optional[str] = Query(None, description="Filter: pending | approved | rejected"),
    authorization: Optional[str] = Header(None)
):
    """Admin: Get all customer style submissions for moderation."""
    _require_admin(authorization)
    return style_gallery_service.get_all_style_submissions(status=status)


@router.put("/admin/submissions/{submission_id}/approve", response_model=StyleSubmissionResponse)
def approve_submission(submission_id: str, authorization: Optional[str] = Header(None)):
    """Admin: Approve customer photo for public gallery display."""
    _require_admin(authorization)
    updated = style_gallery_service.approve_style_submission(submission_id)
    if not updated:
        raise HTTPException(status_code=404, detail="Submission not found")
    return updated


@router.put("/admin/submissions/{submission_id}/reject", response_model=StyleSubmissionResponse)
def reject_submission(submission_id: str, authorization: Optional[str] = Header(None)):
    """Admin: Reject customer photo."""
    _require_admin(authorization)
    updated = style_gallery_service.reject_style_submission(submission_id)
    if not updated:
        raise HTTPException(status_code=404, detail="Submission not found")
    return updated


@router.delete("/admin/submissions/{submission_id}")
def delete_submission(submission_id: str, authorization: Optional[str] = Header(None)):
    """Admin: Delete submission permanently."""
    _require_admin(authorization)
    success = style_gallery_service.delete_style_submission(submission_id)
    if not success:
        raise HTTPException(status_code=404, detail="Submission not found")
    return {"message": "Submission deleted"}
