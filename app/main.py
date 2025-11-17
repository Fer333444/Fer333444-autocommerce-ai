from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import products, orders, health

app = FastAPI(
    title="AutoCommerce AI",
    version="1.0.0",
    description="Backend mínimo de ejemplo para Render usando FastAPI."
)

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers (todos bajo /api/)
app.include_router(health.router, prefix="/api")
app.include_router(products.router, prefix="/api")
app.include_router(orders.router, prefix="/api")

# Ruta raíz
@app.get("/")
async def root():
    return {"message": "AutoCommerce AI está funcionando correctamente 🚀"}
