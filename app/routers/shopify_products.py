# app/routers/shopify_products.py

from fastapi import APIRouter
import os
import requests

router = APIRouter(
    prefix="/shopify",
    tags=["Shopify Products"]
)

SHOPIFY_ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")
SHOPIFY_STORE_URL = os.getenv("SHOPIFY_STORE_URL")


# ---------------------------------------------------------
# CREAR PRODUCTO EN SHOPIFY
# ---------------------------------------------------------
@router.get("/test")
def test_shopify_product():
    """Crea un producto de prueba en Shopify"""

    if not SHOPIFY_ACCESS_TOKEN or not SHOPIFY_STORE_URL:
        return {"error": "Missing Shopify environment variables"}

    api_url = f"https://{SHOPIFY_STORE_URL}/admin/api/2024-07/products.json"

    payload = {
        "product": {
            "title": "Producto Autocommerce AI (Test)",
            "body_html": "Creado automáticamente desde FastAPI.",
            "variants": [{ "price": "19.99" }],
            "images": [{
                "src": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/No_image_available.svg/1024px-No_image_available.svg.png"
            }]
        }
    }

    headers = {
        "X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN,
        "Content-Type": "application/json"
    }

    response = requests.post(api_url, json=payload, headers=headers)

    return {
        "status": "ok",
        "result": response.json()
    }
