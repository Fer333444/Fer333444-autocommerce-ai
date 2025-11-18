from fastapi import APIRouter, Request, Header, HTTPException
import hmac
import hashlib
import base64
import json
import os
from dotenv import load_dotenv
from sqlalchemy import insert
from database import orders_table, order_items_table, raw_webhook_table, database

load_dotenv()

router = APIRouter()

# -------------------------------
#  HMAC VERIFICATION
# -------------------------------
SHOPIFY_WEBHOOK_SECRET = os.getenv("SHOPIFY_WEBHOOK_SECRET")

def verify_webhook(data: bytes, hmac_header: str) -> bool:
    digest = hmac.new(
        SHOPIFY_WEBHOOK_SECRET.encode("utf-8"),
        data,
        hashlib.sha256
    ).digest()

    calculated_hmac = base64.b64encode(digest).decode()
    return hmac.compare_digest(calculated_hmac, hmac_header)


# ========================================
# 1️⃣ WEBHOOK — ORDER CREATED
# ========================================
@router.post("/shopify/webhooks/orders/create")
async def orders_create(request: Request, x_shopify_hmac_sha256: str = Header(None)):
    body = await request.body()

    if not verify_webhook(body, x_shopify_hmac_sha256):
        raise HTTPException(status_code=401, detail="Invalid HMAC")

    data = json.loads(body.decode())
    print("🟩 NUEVO PEDIDO RECIBIDO:", data.get("id"))

    # Guardar copia cruda del webhook
    await database.execute(raw_webhook_table.insert().values(
        event="order_created",
        payload=json.dumps(data)
    ))

    # Insertar pedido
    order_data = {
        "shopify_order_id": data.get("id"),
        "order_number": data.get("order_number"),
        "financial_status": data.get("financial_status")
    }
    order_id = await database.execute(insert(orders_table).values(order_data))

    # Guardar los productos del pedido
    for item in data.get("line_items", []):
        item_data = {
            "order_id": order_id,
            "product_id": item.get("product_id"),
            "variant_id": item.get("variant_id"),
            "title": item.get("title"),
            "quantity": item.get("quantity"),
            "price": item.get("price")
        }
        await database.execute(insert(order_items_table).values(item_data))

    print("🟢 Pedido guardado correctamente.")
    return {"status": "ok"}


# ========================================
# 2️⃣ WEBHOOK — ORDER UPDATED
# ========================================
@router.post("/shopify/webhooks/orders/update")
async def orders_update(request: Request, x_shopify_hmac_sha256: str = Header(None)):
    body = await request.body()

    if not verify_webhook(body, x_shopify_hmac_sha256):
        raise HTTPException(status_code=401, detail="Invalid HMAC")

    data = json.loads(body.decode())
    print("🟦 PEDIDO ACTUALIZADO:", data.get("id"))

    await database.execute(raw_webhook_table.insert().values(
        event="order_updated",
        payload=json.dumps(data)
    ))

    return {"status": "updated"}


# ========================================
# 3️⃣ WEBHOOK — ORDER DELETED
# ========================================
@router.post("/shopify/webhooks/orders/delete")
async def orders_delete(request: Request, x_shopify_hmac_sha256: str = Header(None)):
    body = await request.body()

    if not verify_webhook(body, x_shopify_hmac_sha256):
        raise HTTPException(status_code=401, detail="Invalid HMAC")

    data = json.loads(body.decode())
    print("🟥 PEDIDO ELIMINADO:", data.get("id"))

    await database.execute(raw_webhook_table.insert().values(
        event="order_deleted",
        payload=json.dumps(data)
    ))

    return {"status": "deleted"}


# ========================================
# 4️⃣ WEBHOOK — PRODUCT UPDATED
# ========================================
@router.post("/shopify/webhooks/products/update")
async def products_update(request: Request, x_shopify_hmac_sha256: str = Header(None)):
    body = await request.body()

    if not verify_webhook(body, x_shopify_hmac_sha256):
        raise HTTPException(status_code=401, detail="Invalid HMAC")

    data = json.loads(body.decode())
    print("🟨 PRODUCTO ACTUALIZADO:", data.get("id"))

    await database.execute(raw_webhook_table.insert().values(
        event="product_updated",
        payload=json.dumps(data)
    ))

    return {"status": "product_updated"}
