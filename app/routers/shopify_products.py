from fastapi import APIRouter, Request, Header
import hmac
import hashlib
import base64
import os
import json

router = APIRouter(
    prefix="/shopify",
    tags=["Shopify Webhooks"]
)

SHOPIFY_API_SECRET = os.getenv("SHOPIFY_API_SECRET")


# --------------------------------------------------
# 🛡️ VALIDAR QUE EL WEBHOOK VIENE DE SHOPIFY
# --------------------------------------------------
def verify_webhook(hmac_header: str, body: bytes) -> bool:
    digest = hmac.new(
        SHOPIFY_API_SECRET.encode("utf-8"),
        body,
        hashlib.sha256
    ).digest()

    calculated_hmac = base64.b64encode(digest).decode()

    return hmac.compare_digest(calculated_hmac, hmac_header)


# --------------------------------------------------
# 📦 WEBHOOK — ACTUALIZACIÓN DE PRODUCTO
# --------------------------------------------------
@router.post("/webhook/products/update")
async def webhook_products_update(
    request: Request,
    x_shopify_hmac_sha256: str = Header(None)
):
    body = await request.body()

    # 1. Validar firma
    if not verify_webhook(x_shopify_hmac_sha256, body):
        return {"status": "error", "message": "Invalid HMAC"}

    # 2. Convertir JSON
    data = json.loads(body)

    product_id = data.get("id")
    title = data.get("title")

    print("📦 Webhook recibido: PRODUCT UPDATE")
    print(f"ID: {product_id}")
    print(f"Título: {title}")

    return {"status": "ok", "product_id": product_id, "title": title}
