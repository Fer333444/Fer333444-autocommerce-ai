from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from app.database import Base, engine
from app.routers import (
    shopify_webhook,
    shopify_products_webhook,
    admin_orders,
    admin_products,
    products,
    orders
)

# ============================================================
# 🚀 INICIALIZACIÓN DE LA APP
# ============================================================
app = FastAPI(title="Autocommerce AI", version="1.0")

# ============================================================
# 🧱 CREAR TABLAS AUTOMÁTICAMENTE EN NEON
# ============================================================
Base.metadata.create_all(bind=engine)

# ============================================================
# 🌍 CORS
# ============================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# 🎨 TEMPLATES Y ESTÁTICOS
# ============================================================
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# ============================================================
# 🏠 HOME
# ============================================================
@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# ============================================================
# 🔌 INCLUIR TODOS LOS ROUTERS
# ============================================================
app.include_router(shopify_webhook.router)
app.include_router(shopify_products_webhook.router)
app.include_router(admin_orders.router)
app.include_router(admin_products.router)
app.include_router(products.router)
app.include_router(orders.router)

# ============================================================
# ❤️ HEALTHCHECK
# ============================================================
@app.get("/health")
def health():
    return {"status": "ok"}
