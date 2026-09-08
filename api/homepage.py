# api/homepage.py
#
# Public read endpoint for the customer app's homepage. Editing happens
# through PUT /admin/homepage (admin-only) in api/admin.py.

from fastapi import APIRouter
from app.services import homepage_service

router = APIRouter()


@router.get("/")
def get_homepage():
    """
    Returns the current homepage configuration: announcement bar (with
    a resolved `is_active` flag), hero content, and the enabled/ordered
    section list. Public — no auth required.
    """
    return homepage_service.get_homepage()
