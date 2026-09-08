# app/services/lookbook_service.py

from typing import List, Dict, Any
from datetime import datetime
from app.schemas.lookbook_schema import LookbookCreate, LookbookUpdate, LookbookHotspot
from app.services.firebase_service import get_all, get_one, create_one, update_one, delete_one

def get_all_lookbooks(status: str | None = None) -> List[Dict[str, Any]]:
    lookbooks = get_all("lookbooks")
    if status:
        lookbooks = [l for l in lookbooks if l.get("status") == status]
    return sorted(lookbooks, key=lambda x: x.get("sort_order", 0))


def get_lookbook_by_id(lookbook_id: str) -> Dict[str, Any] | None:
    return get_one("lookbooks", lookbook_id)


def create_lookbook(data: LookbookCreate) -> Dict[str, Any]:
    lb_dict = data.model_dump()
    lb_dict["created_at"] = datetime.utcnow().isoformat()
    return create_one("lookbooks", lb_dict)


def update_lookbook(lookbook_id: str, data: LookbookUpdate) -> Dict[str, Any] | None:
    update_data = data.model_dump(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow().isoformat()
    return update_one("lookbooks", lookbook_id, update_data)


def delete_lookbook(lookbook_id: str) -> bool:
    return delete_one("lookbooks", lookbook_id)


def add_hotspot(lookbook_id: str, hotspot: LookbookHotspot) -> Dict[str, Any] | None:
    lb = get_one("lookbooks", lookbook_id)
    if not lb:
        return None

    hotspots = lb.get("hotspots", [])
    import uuid
    hs_dict = hotspot.model_dump()
    hs_dict["id"] = f"hs_{uuid.uuid4().hex[:8]}"
    hotspots.append(hs_dict)

    update_one("lookbooks", lookbook_id, {"hotspots": hotspots, "updated_at": datetime.utcnow().isoformat()})
    return hs_dict


def remove_hotspot(lookbook_id: str, hotspot_id: str) -> bool:
    lb = get_one("lookbooks", lookbook_id)
    if not lb:
        return False

    hotspots = lb.get("hotspots", [])
    filtered = [h for h in hotspots if h.get("id") != hotspot_id]
    if len(filtered) == len(hotspots):
        return False

    update_one("lookbooks", lookbook_id, {"hotspots": filtered, "updated_at": datetime.utcnow().isoformat()})
    return True
