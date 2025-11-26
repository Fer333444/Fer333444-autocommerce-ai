# app/routers/shopify_webhook.py

from fastapi import APIRouter, Request, Header
import hmac
import hashlib
import base64
import os
import json

router = APIRouter(
    prefix="/webhooks",
    tags=["Shopify Orders Webhooks"]
)

SHOPIFY_API_SECRET = os.getenv("SHOPIFY_API_SECRET")

def verify_hmac(hmac_header: str, body: bytes) -> bool:
    digest = hmac.new(
        SHOPIFY_API_SECRET.encode("utf-8"),
        body,
        hashlib.sha256
    ).digest()

    calculated_hmac = base64.b64encode(digest).decode()
    return hmac.compare_digest(calculated_hmac, hmac_header)

# -------------------------------------------------------
# 🛒 ORDER CREATED
# -------------------------------------------------------
@router.post("/orders/create")
async def order_created(
    request: Request,
    x_shopify_hmac_sha256: str = Header(None)
):
    body = await request.body()

    if not verify_hmac(x_shopify_hmac_sha256, body):
        return {"status": "error", "message": "Invalid HMAC"}

    data = json.loads(body)

    print("🛒 Webhook recibido: ORDER CREATED")
    print(json.dumps(data, indent=2))

    return {"status": "ok"}

# -------------------------------------------------------
# ❌ ORDER DELETED
# -------------------------------------------------------
@router.post("/orders/delete")
async def order_deleted(
    request: Request,
    x_shopify_hmac_sha256: str = Header(None)
):
    body = await request.body()

    if not verify_hmac(x_shopify_hmac_sha256, body):
        return {"status": "error", "message": "Invalid HMAC"}

    data = json.loads(body)

    print("🗑 Webhook recibido: ORDER DELETED")
    print(json.dumps(data, indent=2))

    return {"status": "ok"}
