# app/core/config.py
# 
# This file loads all environment variables using pydantic-settings.
# Every setting has a default so the app doesn't crash during development.
# In production, these are set as environment variables in Vercel dashboard.

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # ── App Info ────────────────────────────────────────────────────────────
    APP_NAME: str = "Noor's Attire API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # ── Firebase ────────────────────────────────────────────────────────────
    # These come from your Firebase serviceAccountKey.json
    FIREBASE_PROJECT_ID: str = ""
    FIREBASE_PRIVATE_KEY_ID: str = ""
    FIREBASE_PRIVATE_KEY: str = ""
    FIREBASE_CLIENT_EMAIL: str = ""
    FIREBASE_CLIENT_ID: str = ""
    FIREBASE_STORAGE_BUCKET: str = ""

    # ── Security ────────────────────────────────────────────────────────────
    SECRET_KEY: str = "dev-secret-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    class Config:
        env_file = ".env"
        extra = "ignore"


# Single instance used throughout the app
settings = Settings()