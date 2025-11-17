from fastapi import APIRouter, Request, Header, HTTPException
import hmac
import hashlib
import base64
import json
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

# 🔐 Importante: la clave real NO va aquí
# Se carga desde las variables de entorno
SHOPIFY_WEBHOOK_SECRET = os.getenv("SHOPIFY_WEBHOOK_SECRET")

if not SHOPIFY_WEBHOOK_SECRET:
    raise Exception("❌ ERROR: Falta la variable de entorno SHOPIFY_WEBHOOK_SECRET en Render.")


def verify_webhook(data: bytes, hmac_header: str) -> bool:
    digest = hmac.new(
        SHOPIFY_WEBHOOK_SECRET.encode("utf-8"),
        data,
        hashlib.sha256
    ).digest()

    calculated_hmac = base64.b64encode(digest).decode()
    return hmac.compare_digest(calculated_hmac, hmac_header)


@router.post("/webhooks/orders/create")
async def orders_create(
    request: Request,
    x_shopify_hmac_sha256: str = Header(None)
):
    body = await request.body()

    if not verify_webhook(body, x_shopify_hmac_sha256):
        raise HTTPException(status_code=401, detail="Invalid HMAC")

    data = json.loads(body.decode())
    print("🛒 Nuevo pedido recibido desde Shopify:")
    print(json.dumps(data, indent=4))

    return {"status": "ok"}


@router.post("/webhooks/products/update")
async def products_update(
    request: Request,
    x_shopify_hmac_sha256: str = Header(None)
):
    body = await request.body()

    if not verify_webhook(body, x_shopify_hmac_sha256):
        raise HTTPException(status_code=401, detail="Invalid HMAC")

    data = json.loads(body.decode())
    print("📦 Producto actualizado desde Shopify:")
    print(json.dumps(data, indent=4))

    return {"status": "ok"}
