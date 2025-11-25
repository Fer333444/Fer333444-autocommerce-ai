from fastapi import APIRouter
import os
import requests

router = APIRouter(
    prefix="/shopify",
    tags=["Shopify"]
)

# ---------------------------------------------------------
#  CARGAR VARIABLES DE ENTORNO (Render)
# ---------------------------------------------------------
SHOPIFY_API_KEY = os.getenv("SHOPIFY_API_KEY")
SHOPIFY_API_SECRET = os.getenv("SHOPIFY_API_SECRET")
SHOPIFY_ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")
SHOPIFY_STORE_URL = os.getenv("SHOPIFY_STORE_URL")


# ---------------------------------------------------------
#  CLIENTE PARA CREAR PRODUCTOS EN SHOPIFY
# ---------------------------------------------------------
def create_shopify_product(title: str, description: str, price: float, image_url: str = None):

    if not SHOPIFY_ACCESS_TOKEN or not SHOPIFY_STORE_URL:
        return {"error": "Variables de entorno de Shopify no configuradas"}

    api_url = f"https://{SHOPIFY_STORE_URL}/admin/api/2024-07/products.json"

    payload = {
        "product": {
            "title": title,
            "body_html": description,
            "variants": [
                {
                    "price": str(price)
                }
            ]
        }
    }

    if image_url:
        payload["product"]["images"] = [{"src": image_url}]

    headers = {
        "X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN,
        "Content-Type": "application/json"
    }

    response = requests.post(api_url, json=payload, headers=headers)

    try:
        return response.json()
    except:
        return {"error": "No se pudo procesar la respuesta de Shopify"}


# ---------------------------------------------------------
#  ENDPOINT DE PRUEBA
# ---------------------------------------------------------
@router.get("/test")
def test_shopify_product():
    """Crea un producto de prueba en Shopify para confirmar conexión"""

    product = create_shopify_product(
        title="Producto Autocommerce AI (Prueba)",
        description="Este producto fue creado automáticamente desde FastAPI en Render.",
        price=19.99,
        image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/No_image_available.svg/1024px-No_image_available.svg.png"
    )

    return {
        "status": "OK",
        "result": product
    }
