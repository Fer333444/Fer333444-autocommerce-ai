from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from app.database import engine, Base, get_db

# IMPORTS CORREGIDOS
from app.routers import admin_panel
from app.routers import shopify_webhooks
from app.routers import shopify_products   # <-- este sí lo añadiste tú

# ---------------------------------------------------------
#  CREAR TABLAS EN LA BASE DE DATOS
# ---------------------------------------------------------
Base.metadata.create_all(bind=engine)

# ---------------------------------------------------------
#  INICIAR FASTAPI
# ---------------------------------------------------------
app = FastAPI(
    title="Autocommerce AI Backend",
    description="Sistema de pedidos + Webhook + Panel Admin",
    version="1.0"
)

# ---------------------------------------------------------
#  PLANTILLAS HTML
# ---------------------------------------------------------
templates = Jinja2Templates(directory="app/templates")

# ---------------------------------------------------------
#  MONTAR CARPETA STATIC
# ---------------------------------------------------------
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# ---------------------------------------------------------
#  INCLUIR ROUTERS
# ---------------------------------------------------------
app.include_router(admin_panel.router)
app.include_router(shopify_webhooks.router)
app.include_router(shopify_products.router)

# ---------------------------------------------------------
#  RUTA PRINCIPAL
# ---------------------------------------------------------
@app.get("/")
def home():
    return {
        "status": "ok",
        "message": "Autocommerce AI Backend funcionando correctamente 🧠⚡",
        "docs": "/docs",
        "admin_panel": "/admin/orders"
    }

# ---------------------------------------------------------
#  HEALTH CHECK
# ---------------------------------------------------------
@app.get("/health")
def health():
    return {"status": "healthy"}
 	