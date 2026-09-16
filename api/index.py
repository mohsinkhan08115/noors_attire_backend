# api/index.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

from api.products       import router as products_router
from api.auth           import router as auth_router
from api.orders         import router as orders_router
from api.users          import router as users_router
from api.admin          import router as admin_router
from api.wishlist       import router as wishlist_router
from api.homepage       import router as homepage_router
from api.variants       import router as variants_router
from api.looks          import router as looks_router
from api.lookbooks      import router as lookbooks_router
from api.alerts         import router as alerts_router
from api.style_gallery  import router as style_gallery_router

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Backend API for Noor's Attire — Pashtun Dresses & Paint Shirts",
    docs_url="/docs",
    redoc_url="/redoc",
)

from starlette.datastructures import Headers
from starlette.responses import Response

class RobustCORSMiddleware(CORSMiddleware):
    def preflight_response(self, request_headers: Headers) -> Response:
        response = super().preflight_response(request_headers)
        response.headers["Access-Control-Allow-Private-Network"] = "true"
        return response

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            async def send_with_pna(message):
                if message["type"] == "http.response.start":
                    headers = list(message.get("headers", []))
                    headers.append((b"access-control-allow-private-network", b"true"))
                    message["headers"] = headers
                await send(message)
            await super().__call__(scope, receive, send_with_pna)
        else:
            await super().__call__(scope, receive, send)

app.add_middleware(
    RobustCORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.staticfiles import StaticFiles
import os

# Ensure the uploads directory exists
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(products_router,      prefix="/products",      tags=["Products"])
app.include_router(auth_router,          prefix="/auth",          tags=["Authentication"])
app.include_router(orders_router,        prefix="/orders",        tags=["Orders"])
app.include_router(users_router,         prefix="/users",         tags=["Users"])
app.include_router(admin_router,         prefix="/admin",         tags=["Admin"])
app.include_router(wishlist_router,      prefix="/wishlist",      tags=["Wishlist"])
app.include_router(homepage_router,      prefix="/homepage",      tags=["Homepage"])
app.include_router(variants_router,      prefix="/products",      tags=["Variants"])
app.include_router(looks_router,         prefix="/looks",         tags=["Looks"])
app.include_router(lookbooks_router,     prefix="/lookbooks",     tags=["Lookbooks"])
app.include_router(alerts_router,        prefix="/alerts",        tags=["Alerts"])
app.include_router(style_gallery_router, prefix="/style-gallery", tags=["Style Gallery"])

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