# app/services/look_service.py

from typing import List, Dict, Any
from datetime import datetime
from app.schemas.look_schema import LookCreate, LookUpdate
from app.services.firebase_service import get_all, get_one, create_one, update_one, delete_one

def get_all_looks(status: str | None = None) -> List[Dict[str, Any]]:
    looks = get_all("looks")
    if status:
        return [l for l in looks if l.get("status") == status]
    return looks


def get_look_by_id(look_id: str) -> Dict[str, Any] | None:
    return get_one("looks", look_id)


def create_look(data: LookCreate) -> Dict[str, Any]:
    look_dict = data.model_dump()
    look_dict["created_at"] = datetime.utcnow().isoformat()
    return create_one("looks", look_dict)


def update_look(look_id: str, data: LookUpdate) -> Dict[str, Any] | None:
    update_data = data.model_dump(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow().isoformat()
    return update_one("looks", look_id, update_data)


def delete_look(look_id: str) -> bool:
    return delete_one("looks", look_id)
