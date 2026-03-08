# app/services/firebase_service.py
#
# Firebase connection using Realtime Database (free, no billing needed!)
# Realtime Database stores data as JSON tree structure.

import firebase_admin
from firebase_admin import credentials, db, storage
from app.core.config import settings


def _init_firebase():
    """Initialize Firebase only once."""
    if firebase_admin._apps:
        return

    cred_dict = {
        "type": "service_account",
        "project_id": settings.FIREBASE_PROJECT_ID,
        "private_key_id": settings.FIREBASE_PRIVATE_KEY_ID,
        "private_key": settings.FIREBASE_PRIVATE_KEY.replace("\\n", "\n"),
        "client_email": settings.FIREBASE_CLIENT_EMAIL,
        "client_id": settings.FIREBASE_CLIENT_ID,
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
    }

    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred, {
        "databaseURL": settings.FIREBASE_DATABASE_URL,
        "storageBucket": settings.FIREBASE_STORAGE_BUCKET,
    })


_init_firebase()


# ── Helper functions ──────────────────────────────────────────────────────────

def _fix_lists(data: dict) -> dict:
    """
    Firebase Realtime Database converts Python lists to dicts with numeric keys.
    e.g. ["a", "b"] becomes {"0": "a", "1": "b"} or {3: "url"} for sparse arrays.
    This function converts them back to proper Python lists.
    """
    for key, value in data.items():
        if isinstance(value, dict) and all(str(k).isdigit() for k in value.keys()):
            # Convert numeric-keyed dict back to list, sorted by key
            data[key] = [value[k] for k in sorted(value.keys(), key=lambda x: int(x))]
        elif isinstance(value, dict):
            data[key] = _fix_lists(value)
    return data


def get_all(collection: str) -> list:
    """Get all records from a collection. Returns list of dicts with 'id' field."""
    ref = db.reference(collection)
    data = ref.get()
    if not data:
        return []
    return [_fix_lists({"id": k, **v}) for k, v in data.items()]


def get_one(collection: str, doc_id: str) -> dict | None:
    """Get a single record by ID."""
    ref = db.reference(f"{collection}/{doc_id}")
    data = ref.get()
    if not data:
        return None
    return _fix_lists({"id": doc_id, **data})


def create_one(collection: str, data: dict) -> dict:
    """Create a new record. Returns data with auto-generated ID."""
    ref = db.reference(collection)
    new_ref = ref.push(data)   # push() auto-generates unique ID
    return {"id": new_ref.key, **data}


def update_one(collection: str, doc_id: str, data: dict) -> dict | None:
    """Update specific fields of a record."""
    ref = db.reference(f"{collection}/{doc_id}")
    if not ref.get():
        return None
    ref.update(data)
    updated = ref.get()
    return _fix_lists({"id": doc_id, **updated})


def delete_one(collection: str, doc_id: str) -> bool:
    """Delete a record. Returns True if existed."""
    ref = db.reference(f"{collection}/{doc_id}")
    if not ref.get():
        return False
    ref.delete()
    return True


def query_by_field(collection: str, field: str, value) -> list:
    """Query records where field equals value."""
    ref = db.reference(collection)
    data = ref.order_by_child(field).equal_to(value).get()
    if not data:
        return []
    return [_fix_lists({"id": k, **v}) for k, v in data.items()]


def upload_image(file_data: bytes, filename: str, content_type: str = "image/jpeg") -> str:
    """Upload image to Firebase Storage. Returns public URL."""
    from firebase_admin import storage as fb_storage
    bucket = fb_storage.bucket()
    blob = bucket.blob(f"products/{filename}")
    blob.upload_from_string(file_data, content_type=content_type)
    blob.make_public()
    return blob.public_url