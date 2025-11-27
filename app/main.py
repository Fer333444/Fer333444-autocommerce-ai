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
# 🚀 INICIALIZACIÓN
# ============================================================
app = FastAPI(
    title="Autocommerce AI Backend",
    version="1.0.0"
)

# ============================================================
# 🧱 CREAR TABLAS
# ============================================================
Base.metadata.create_all(bind=engine)

# ============================================================
# 🌍 CORS
# ============================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# 🎨 TEMPLATES Y STATIC (CORREGIDO)
# ============================================================
templates = Jinja2Templates(directory="templates")  # 👈 CORREGIDO
app.mount("/static", StaticFiles(directory="static"), name="static")  # 👈 CORREGIDO

# ============================================================
# 🏠 HOME
# ============================================================
@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "admin_products": "/admin/products",
            "admin_orders": "/admin/orders",
            "status": "ok"
        }
    )

# ============================================================
# ❤️ HEALTHCHECK
# ============================================================
@app.get("/health")
def health():
    return {"status": "healthy"}

# ============================================================
# 🔌 ROUTERS
# ============================================================
app.include_router(shopify_webhook_router, prefix="/shopify")
app.include_router(shopify_products_webhook_router, prefix="/shopify")
app.include_router(admin_orders_router, prefix="/admin")
app.include_router(admin_products_router, prefix="/admin")

# ============================================================
# 🧪 TEST WEBHOOK
# ============================================================
@app.get("/shopify/test")
def webhook_test():
    return {"message": "Webhook endpoint activo 🎉", "status": "ok"}
