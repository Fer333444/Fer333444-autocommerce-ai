# app/main.py

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.database import Base, engine

# Routers
from app.routers.shopify_webhook import router as shopify_webhook_router
from app.routers.shopify_products_webhook import router as shopify_products_webhook_router
from app.routers.admin_orders import router as admin_orders_router
from app.routers.admin_products import router as admin_products_router

# ============================================================
# 🚀 INICIALIZACIÓN DE LA APP
# ============================================================
app = FastAPI(
    title="Autocommerce AI Backend",
    description="Sistema completo Shopify + Webhooks + Panel Admin",
    version="1.0.0"
)

# ============================================================
# 🧱 CREAR TABLAS AUTOMÁTICAMENTE EN NEON
# ============================================================
Base.metadata.create_all(bind=engine)

# ============================================================
# 🌍 CORS (OBLIGATORIO PARA RENDER + SHOPIFY)
# ============================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# 🎨 TEMPLATES Y ARCHIVOS ESTÁTICOS (CORREGIDO)
# ============================================================
# 👉 Importante: tu estructura es /app/main.py, por eso las rutas deben ser "app/templates"
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# ============================================================
# 🏠 HOME
# ============================================================
@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "status": "online",
            "admin_products": "/admin/products",
            "admin_orders": "/admin/orders",
            "webhook_test": "/shopify/test"
        }
    )

# ============================================================
# ❤️ HEALTHCHECK
# ============================================================
@app.get("/health")
def health():
    return {"status": "healthy", "service": "autocommerce-ai"}

# ============================================================
# 🔌 ROUTERS (DEBES TENER ESTO ASÍ)
# ============================================================
app.include_router(shopify_webhook_router, prefix="/shopify")
app.include_router(shopify_products_webhook_router, prefix="/shopify")
app.include_router(admin_orders_router, prefix="/admin")
app.include_router(admin_products_router, prefix="/admin")

# ============================================================
# 🧪 TEST ENDPOINT (DEVUELVE 200)
# ============================================================
@app.get("/shopify/test")
def webhook_test():
    return {"message": "Webhook endpoint activo 🎉", "status": "ok"}

# ============================================================
# FIN DEL MAIN
# ============================================================
