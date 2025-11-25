# app/main.py

from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from app.database import engine, Base

# Routers
from app.routers import (
    admin_orders,
    shopify_webhook,
    shopify_products
)

# ---------------------------------------------------------
#  CREAR TABLAS EN LA BASE DE DATOS
# ---------------------------------------------------------
Base.metadata.create_all(bind=engine)

# ---------------------------------------------------------
#  INICIAR FASTAPI
# ---------------------------------------------------------
app = FastAPI(
    title="Autocommerce AI Backend",
    description="Sistema de pedidos + Webhook + Panel Admin + Productos Shopify",
    version="1.0"
)

# ---------------------------------------------------------
#  PLANTILLAS HTML
# ---------------------------------------------------------
templates = Jinja2Templates(directory="app/templates")

# ---------------------------------------------------------
#  ARCHIVOS ESTÁTICOS
# ---------------------------------------------------------
# (Esta carpeta ya existe gracias al .gitkeep)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# ---------------------------------------------------------
#  INCLUIR ROUTERS
# ---------------------------------------------------------
app.include_router(admin_orders.router)      # Panel admin de pedidos
app.include_router(shopify_webhook.router)   # Webhooks de Shopify
app.include_router(shopify_products.router)  # Creación/envío de productos a Shopify

# ---------------------------------------------------------
#  RUTA PRINCIPAL
# ---------------------------------------------------------
@app.get("/")
def home():
    return {
        "status": "ok",
        "message": "Autocommerce AI Backend funcionando correctamente 🧠⚡",
        "docs": "/docs",
        "admin_panel": "/admin/orders",
        "shopify_test_product": "/shopify/test"
    }

# ---------------------------------------------------------
#  HEALTH CHECK
# ---------------------------------------------------------
@app.get("/health")
def health():
    return {"status": "healthy"}
