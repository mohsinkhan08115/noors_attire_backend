# api/index.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

from api.products import router as products_router
from api.auth     import router as auth_router
from api.orders   import router as orders_router
from api.users    import router as users_router
from api.admin    import router as admin_router

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Backend API for Noor's Attire — Pashtun Dresses & Paint Shirts",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products_router, prefix="/products", tags=["Products"])
app.include_router(auth_router,     prefix="/auth",     tags=["Authentication"])
app.include_router(orders_router,   prefix="/orders",   tags=["Orders"])
app.include_router(users_router,    prefix="/users",    tags=["Users"])
app.include_router(admin_router,    prefix="/admin",    tags=["Admin"])

@app.get("/", tags=["Health"])
def root():
    return {
        "app":     settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status":  "running",
        "docs":    "/docs",
    }

@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}