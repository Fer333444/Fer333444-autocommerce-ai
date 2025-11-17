from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

# Routers
from app.routers.health import router as health_router
from app.routers.products import router as products_router
from app.routers.orders import router as orders_router
from app.routers.shopify_webhooks import router as shopify_router

load_dotenv()

app = FastAPI(
    title="AutoCommerce AI",
    description="Backend conectado a Shopify + Frontend Next.js",
    version="1.0.0"
)

# ===========================
# CORS (Permitir Next.js)
# ===========================

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "*"],   # Durante desarrollo permitimos todo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===========================
# Registrar Routers
# ===========================

app.include_router(health_router, prefix="/api")
app.include_router(products_router, prefix="/api")
app.include_router(orders_router, prefix="/api")

# Shopify webhooks van SIN autenticación del frontend
# solo con verificación HMAC
app.include_router(shopify_router, prefix="/api/shopify")

# ===========================
# Ruta raíz
# ===========================

@app.get("/")
def root():
    return {"message": "AutoCommerce AI está funcionando correctamente 🚀"}
