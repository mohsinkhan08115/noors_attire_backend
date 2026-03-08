# app/services/firebase_service.py
#
# This file initializes Firebase Admin SDK.
# Firebase Admin SDK lets our backend talk to Firestore (database),
# Firebase Storage (images), and Firebase Auth (user management).
#
# We initialize it ONCE here and import `db` and `bucket` everywhere else.

import firebase_admin
from firebase_admin import credentials, firestore, storage, auth
from app.core.config import settings


def _init_firebase():
    """
    Initialize Firebase only once.
    If already initialized, skip to avoid errors.
    """
    if firebase_admin._apps:
        return  # Already initialized

    # Build credentials dict from environment variables
    # This avoids needing the serviceAccountKey.json file in production
    cred_dict = {
        "type": "service_account",
        "project_id": settings.FIREBASE_PROJECT_ID,
        "private_key_id": settings.FIREBASE_PRIVATE_KEY_ID,
        # Replace literal \n with actual newlines in the private key
        "private_key": settings.FIREBASE_PRIVATE_KEY.replace("\\n", "\n"),
        "client_email": settings.FIREBASE_CLIENT_EMAIL,
        "client_id": settings.FIREBASE_CLIENT_ID,
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
    }

    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred, {
        "storageBucket": settings.FIREBASE_STORAGE_BUCKET
    })


# Initialize on import
_init_firebase()

# These are the main objects we use throughout the app:
# db  → Firestore database client (read/write documents)
# bucket → Firebase Storage bucket (upload/download images)
db = firestore.client()
bucket = storage.bucket()
firebase_auth = auth


def get_collection(name: str):
    """Helper to get a Firestore collection reference."""
    return db.collection(name)


def get_document(collection: str, doc_id: str):
    """Helper to get a single Firestore document."""
    doc = db.collection(collection).document(doc_id).get()
    if doc.exists:
        data = doc.to_dict()
        data["id"] = doc.id
        return data
    return None


def upload_image(file_data: bytes, filename: str, content_type: str = "image/jpeg") -> str:
    """
    Upload an image to Firebase Storage and return its public URL.
    
    Images are stored under: products/filename
    They are made publicly readable so the frontend can display them.
    
    Returns: Public URL string
    """
    blob = bucket.blob(f"products/{filename}")
    blob.upload_from_string(file_data, content_type=content_type)
    blob.make_public()
    return blob.public_url