# app/main.py

from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from app.database import engine, Base

# Importar routers
from app.routers import (
    admin_orders,
    admin_products,
    shopify_webhook,              # Webhooks de órdenes
    shopify_products_webhook,     # Webhooks de productos
    shopify_products              # API Shopify (test)
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
    description="Sistema de Pedidos + Webhooks Shopify + Panel Admin",
    version="1.0"
)

# ---------------------------------------------------------
#  PLANTILLAS HTML
# ---------------------------------------------------------
templates = Jinja2Templates(directory="app/templates")

# ---------------------------------------------------------
#  ARCHIVOS ESTÁTICOS
# ---------------------------------------------------------
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# ---------------------------------------------------------
#  INCLUIR ROUTERS
# ---------------------------------------------------------
app.include_router(admin_orders.router)           # Panel de pedidos
app.include_router(admin_products.router)         # Panel de productos
app.include_router(shopify_webhook.router)        # Webhooks órdenes
app.include_router(shopify_products_webhook.router)  # Webhooks productos
app.include_router(shopify_products.router)       # API Shopify (test endpoint)

# ---------------------------------------------------------
#  RUTA PRINCIPAL
# ---------------------------------------------------------
@app.get("/")
def home():
    return {
        "status": "ok",
        "message": "Autocommerce AI Backend funcionando correctamente 🧠⚡",
        "docs": "/docs",
        "admin_orders": "/admin/orders",
        "admin_products": "/admin/products",
        "shopify_test_product": "/shopify/test",
        "webhooks": {
            "order_create": "/webhooks/orders/create",
            "order_delete": "/webhooks/orders/delete",
            "product_update": "/shopify/webhook/products/update"
        }
    }

# ---------------------------------------------------------
#  HEALTH CHECK
# ---------------------------------------------------------
@app.get("/health")
def health():
    return {"status": "healthy"}
