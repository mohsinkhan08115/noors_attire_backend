# api/index.py
#
# This is the main entry point for the FastAPI application.
# Vercel looks for this file and runs it as a serverless function.
#
# All routes are registered here from separate route files.
# CORS is configured to allow requests from the Flutter web frontend.

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

# Import all route modules
from api.products import router as products_router
from api.auth import router as auth_router
from api.orders import router as orders_router
from api.users import router as users_router

# Create the FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Backend API for Noor's Attire — Pashtun Dresses & Paint Shirts",
    docs_url="/docs",        # Swagger UI at /docs
    redoc_url="/redoc",      # ReDoc at /redoc
)

# ── CORS Configuration ───────────────────────────────────────────────────────
# CORS (Cross-Origin Resource Sharing) allows the Flutter web app
# running on one domain to call this API on another domain.
# In production, replace "*" with your actual frontend domain.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # Change to ["https://noors-attire.vercel.app"] in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register Routes ──────────────────────────────────────────────────────────
# Each router handles a group of related endpoints.
# prefix="/products" means all routes in products.py start with /products

app.include_router(products_router, prefix="/products", tags=["Products"])
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(orders_router, prefix="/orders", tags=["Orders"])
app.include_router(users_router, prefix="/users", tags=["Users"])


@app.get("/", tags=["Health"])
def root():
    """Health check endpoint. Vercel pings this to verify the app is running."""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}