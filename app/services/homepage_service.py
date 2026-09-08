# app/services/homepage_service.py
#
# Single homepage configuration document. Resolves the announcement's
# scheduled active window server-side so the frontend just checks one
# boolean rather than duplicating timezone/clock logic on the client.

from datetime import datetime
from typing import Optional
from app.services.firebase_service import get_one, set_one
from app.schemas.homepage_schema import HomepageConfig

COLLECTION = "homepage"
DOC_ID = "config"


def get_homepage() -> dict:
    saved = get_one(COLLECTION, DOC_ID)
    config = HomepageConfig(**saved) if saved else HomepageConfig()
    data = config.model_dump()

    ann = data["announcement"]
    ann["is_active"] = _is_announcement_active(
        ann["enabled"], ann.get("start_at"), ann.get("end_at")
    )
    return data


def update_homepage(config: HomepageConfig) -> dict:
    data = config.model_dump()
    data["updated_at"] = datetime.utcnow().isoformat()
    set_one(COLLECTION, DOC_ID, data)
    return get_homepage()


def _is_announcement_active(
    enabled: bool, start_at: Optional[str], end_at: Optional[str]
) -> bool:
    if not enabled:
        return False
    now = datetime.utcnow()
    if start_at:
        try:
            if now < datetime.fromisoformat(start_at):
                return False
        except ValueError:
            pass
    if end_at:
        try:
            if now > datetime.fromisoformat(end_at):
                return False
        except ValueError:
            pass
    return True
