from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

# IMPORTS CORREGIDOS
from app.database import engine, SessionLocal
from app.models import Base
from app.routers import shopify_webhooks

import logging

# Logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear tablas en Neon automáticamente
Base.metadata.create_all(bind=engine)

# Inicializar FastAPI
app = FastAPI()

# Templates (si usas vistas)
templates = Jinja2Templates(directory="app/templates")


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return "<h1>🚀 AutoCommerce-AI funcionando correctamente</h1>"


# Registrar el router de Shopify
app.include_router(
    shopify_webhooks.router,
    prefix="/api/shopify",
    tags=["Shopify Webhooks"]
)
