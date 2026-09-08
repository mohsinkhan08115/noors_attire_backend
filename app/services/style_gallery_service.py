# app/services/style_gallery_service.py

from typing import List, Dict, Any
from datetime import datetime
from app.schemas.style_gallery_schema import StyleSubmissionCreate
from app.services.firebase_service import get_all, get_one, create_one, update_one, delete_one

def submit_style_photo(user_id: str | None, data: StyleSubmissionCreate) -> Dict[str, Any]:
    submission = {
        "user_id": user_id,
        "image_url": data.image_url,
        "caption": data.caption,
        "product_id": data.product_id,
        "customer_name": data.customer_name or "Anonymous Patron",
        "status": "pending",
        "created_at": datetime.utcnow().isoformat()
    }
    return create_one("style_submissions", submission)


def get_public_style_gallery() -> List[Dict[str, Any]]:
    submissions = get_all("style_submissions")
    approved = [s for s in submissions if s.get("status") == "approved"]
    return sorted(approved, key=lambda x: x.get("created_at", ""), reverse=True)


def get_all_style_submissions(status: str | None = None) -> List[Dict[str, Any]]:
    submissions = get_all("style_submissions")
    if status:
        submissions = [s for s in submissions if s.get("status") == status]
    return sorted(submissions, key=lambda x: x.get("created_at", ""), reverse=True)


def approve_style_submission(submission_id: str) -> Dict[str, Any] | None:
    return update_one("style_submissions", submission_id, {
        "status": "approved",
        "updated_at": datetime.utcnow().isoformat()
    })


def reject_style_submission(submission_id: str) -> Dict[str, Any] | None:
    return update_one("style_submissions", submission_id, {
        "status": "rejected",
        "updated_at": datetime.utcnow().isoformat()
    })


def delete_style_submission(submission_id: str) -> bool:
    return delete_one("style_submissions", submission_id)
