# app/routers/shopify_webhook.py

from fastapi import APIRouter, Request, Header
import hmac
import hashlib
import base64
import os
import json

from sqlalchemy.orm import Session
from app.database import get_db

# IMPORTAMOS TUS MODELOS REALES
from app.models import Order, OrderItem

router = APIRouter(
    prefix="/shopify",
    tags=["Shopify Webhooks"]
)

SHOPIFY_API_SECRET = os.getenv("SHOPIFY_API_SECRET")

# -----------------------------------------------------------
# 🛡️ Validación de la firma HMAC
# -----------------------------------------------------------
def verify_webhook(hmac_header: str, body: bytes) -> bool:
    digest = hmac.new(
        SHOPIFY_API_SECRET.encode("utf-8"),
        body,
        hashlib.sha256
    ).digest()

    calculated_hmac = base64.b64encode(digest).decode()
    return hmac.compare_digest(calculated_hmac, hmac_header)


# -----------------------------------------------------------
# 💾 Guardar pedido en la base de datos (Neon)
# -----------------------------------------------------------
def save_order_to_db(db: Session, data: dict):
    shopify_order_id = data.get("id")
    order_number = data.get("order_number")
    financial_status = data.get("financial_status")

    # ¿Ya existe?
    existing_order = db.query(Order).filter(Order.shopify_order_id == shopify_order_id).first()

    if existing_order:
        print(f"⚠️ El pedido ya existe en la DB: {shopify_order_id}")
        return existing_order

    # Crear pedido
    order = Order(
        shopify_order_id=shopify_order_id,
        order_number=str(order_number),
        financial_status=financial_status
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    # Guardar los items
    for item in data.get("line_items", []):
        db_item = OrderItem(
            order_id=order.id,
            product_id=item.get("product_id"),
            variant_id=item.get("variant_id"),
            title=item.get("title"),
            quantity=item.get("quantity"),
            price=item.get("price")
        )
        db.add(db_item)

    db.commit()
    print(f"✅ Pedido guardado en Neon: {shopify_order_id}")

    return order


# -----------------------------------------------------------
# 📦 Webhook: Creación de pedido
# -----------------------------------------------------------
@router.post("/webhooks/orders/create")
async def webhook_orders_create(
    request: Request,
    x_shopify_hmac_sha256: str = Header(None),
    db: Session = next(get_db())
):
    body = await request.body()

    if not verify_webhook(x_shopify_hmac_sha256, body):
        print("❌ HMAC inválido en orders/create")
        return {"status": "error", "message": "Invalid HMAC"}

    data = json.loads(body)

    print("📦 Webhook recibido: ORDER CREATE")
    print(json.dumps(data, indent=2))

    save_order_to_db(db, data)

    return {"status": "ok"}


# -----------------------------------------------------------
# 🔄 Webhook: Actualización de pedido
# -----------------------------------------------------------
@router.post("/webhooks/orders/update")
async def webhook_orders_update(
    request: Request,
    x_shopify_hmac_sha256: str = Header(None),
    db: Session = next(get_db())
):
    body = await request.body()

    if not verify_webhook(x_shopify_hmac_sha256, body):
        print("❌ HMAC inválido en orders/update")
        return {"status": "error", "message": "Invalid HMAC"}

    data = json.loads(body)

    print("♻️ Webhook recibido: ORDER UPDATE")
    print(json.dumps(data, indent=2))

    shopify_id = data.get("id")
    order = db.query(Order).filter(Order.shopify_order_id == shopify_id).first()

    if order:
        order.financial_status = data.get("financial_status")
        db.commit()
        print("✔ Pedido actualizado")
    else:
        print("⚠ Pedido no existe, creando…")
        save_order_to_db(db, data)

    return {"status": "ok"}


# -----------------------------------------------------------
# 🗑 Webhook: Eliminación de pedido
# -----------------------------------------------------------
@router.post("/webhooks/orders/delete")
async def webhook_orders_delete(
    request: Request,
    x_shopify_hmac_sha256: str = Header(None),
    db: Session = next(get_db())
):
    body = await request.body()

    if not verify_webhook(x_shopify_hmac_sha256, body):
        print("❌ HMAC inválido en orders/delete")
        return {"status": "error", "message": "Invalid HMAC"}

    data = json.loads(body)
    shopify_id = data.get("id")

    print("🗑 Webhook recibido: ORDER DELETE")

    order = db.query(Order).filter(Order.shopify_order_id == shopify_id).first()
    if order:
        db.delete(order)
        db.commit()
        print(f"✔ Pedido eliminado de Neon: {shopify_id}")
    else:
        print("⚠ Pedido no encontrado para eliminar")

    return {"status": "ok"}


# -----------------------------------------------------------
# 🛍 Webhook: Actualización de producto
# -----------------------------------------------------------
@router.post("/webhooks/products/update")
async def webhook_products_update(
    request: Request,
    x_shopify_hmac_sha256: str = Header(None)
):
    body = await request.body()

    if not verify_webhook(x_shopify_hmac_sha256, body):
        print("❌ HMAC inválido en products/update")
        return {"status": "error", "message": "Invalid HMAC"}

    data = json.loads(body)

    print("🛍 Webhook recibido: PRODUCT UPDATE")
    print(json.dumps(data, indent=2))

    return {"status": "ok"}
