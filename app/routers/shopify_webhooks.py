from fastapi import APIRouter, Request, Header, HTTPException
import hmac
import hashlib
import base64
import json
import os

router = APIRouter()

SHOPIFY_WEBHOOK_SECRET = os.getenv("SHOPIFY_WEBHOOK_SECRET")

def verify_webhook(data: bytes, hmac_header: str) -> bool:
    print("========== DEBUG HMAC ==========")
    print(f"SECRET (first 6 chars): {SHOPIFY_WEBHOOK_SECRET[:6]}******")
    print(f"RAW BODY: {data}")
    print(f"HMAC FROM SHOPIFY: {hmac_header}")

    digest = hmac.new(
        SHOPIFY_WEBHOOK_SECRET.encode('utf-8'),
        data,
        hashlib.sha256
    ).digest()

    calculated_hmac = base64.b64encode(digest).decode()

    print(f"HMAC CALCULATED: {calculated_hmac}")
    print("================================")

    return hmac.compare_digest(calculated_hmac, hmac_header)


@router.post("/webhooks/orders/create")
async def orders_create(request: Request, x_shopify_hmac_sha256: str = Header(None)):
    body = await request.body()

    if not verify_webhook(body, x_shopify_hmac_sha256):
        raise HTTPException(status_code=401, detail="Invalid HMAC")

    data = json.loads(body.decode())
    print("🛒 Nuevo pedido recibido:")
    print(json.dumps(data, indent=4))

    return {"status": "success"}
