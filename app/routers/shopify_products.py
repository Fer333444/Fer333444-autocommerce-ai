# app/routers/shopify_products.py

from fastapi import APIRouter

router = APIRouter(
    prefix="/shopify",
    tags=["Shopify Product API"]
)

@router.get("/test")
def test_shopify_route():
    return {"status": "ok", "message": "Ruta /shopify/test funcionando"}
