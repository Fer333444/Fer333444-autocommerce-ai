from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import products, orders, health, shopify_webhooks

app = FastAPI(
    title="AutoCommerce AI",
    version="1.0.0",
    description="Backend con FastAPI + Shopify + Render."
)

# ---------------------------
#   CORS CONFIGURATION
# ---------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # Puedes restringirlo a tu dominio después
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------
#   ROUTERS
# ---------------------------
app.include_router(health.router)
app.include_router(products.router, prefix="/api")
app.include_router(orders.router, prefix="/api")
app.include_router(shopify_webhooks.router, prefix="/api")   # <<< NUEVO


# ---------------------------
#   ROOT ROUTE
# ---------------------------
@app.get("/")
async def root():
    return {"message": "AutoCommerce AI está funcionando correctamente 🚀"}
