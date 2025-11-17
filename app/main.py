import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import create_db_and_tables
from app.routers import shopify_webhooks

APP_NAME = "AutoCommerce AI – Backend"
APP_VERSION = "1.0.0"

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="Backend centralizado con integración Shopify + Neon + Webhooks"
)

# ----------------------------------------------------------
# CORS: permite que Next.js / Shopify / Frontend accedan
# ----------------------------------------------------------
origins = [
    "*",   # Puedes cambiarlo luego a tu dominio
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------------------------------------
# EVENTO AL INICIAR
# ----------------------------------------------------------
@app.on_event("startup")
def on_startup():
    print("🚀 AutoCommerce AI iniciando...")
    print("🔧 Creando tablas si no existen en Neon...")
    create_db_and_tables()
    print("📦 Conexión a base de datos lista.")
    print("🛒 Shopify Webhooks cargados.")
    print("🌐 Sistema en línea.")

# ----------------------------------------------------------
# HOME
# ----------------------------------------------------------
@app.get("/")
async def home():
    return {
        "message": "AutoCommerce AI Backend activo 🚀",
        "status": "online",
        "version": APP_VERSION,
    }

# ----------------------------------------------------------
# ROUTERS
# ----------------------------------------------------------
app.include_router(
    shopify_webhooks.router,
    prefix="/api/shopify",
    tags=["Shopify Webhooks"]
)
