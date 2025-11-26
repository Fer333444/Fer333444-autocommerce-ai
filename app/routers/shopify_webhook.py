# app/routers/shopify_webhook.py

from fastapi import APIRouter, Request, Header, Depends
import hmac, hashlib, base64, json
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Order, OrderItem
import os

router = APIRouter(prefix="/shopify", tags=["Shopify Webhooks"])

SHOPIFY_API_SECRET = os.getenv("SHOPIFY_API_SECRET")


def verify_webhook(hmac_header: str, body: bytes) -> bool:
    digest = hmac.new(
        SHOPIFY_API_SECRET.encode("utf-8"),
        body,
        hashlib.sha256
    ).digest()

    calculated_hmac = base64.b64encode(digest).decode()
    return hmac.compare_digest(calculated_hmac, hmac_header)


# --------------------------------------------------
# 🔔 WEBHOOK — ORDER CREATED
# --------------------------------------------------
@router.post("/webhooks/orders/create")
async def webhook_orders_create(
    request: Request,
    db: Session = Depends(get_db),
    x_shopify_hmac_sha256: str = Header(None)
):
    body = await request.body()

    # 1️⃣ Validar firma
    if not verify_webhook(x_shopify_hmac_sha256, body):
        return {"status": "error", "message": "Invalid HMAC"}

    data = json.loads(body)

    # 2️⃣ Guardar orden en DB
    order = Order(
        shopify_order_id=data["id"],
        order_number=data.get("order_number", ""),
        financial_status=data.get("financial_status", "")
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    # 3️⃣ Guardar items
    for item in data.get("line_items", []):
        db.add(OrderItem(
            order_id=order.id,
            product_id=item.get("product_id"),
            variant_id=item.get("variant_id"),
            title=item.get("title"),
            quantity=item.get("quantity"),
            price=item.get("price")
        ))

    db.commit()

    return {"status": "ok", "order_id": order.id}


# --------------------------------------------------
# 🔄 WEBHOOK — ORDER UPDATED
# --------------------------------------------------
@router.post("/webhooks/orders/updated")
async def webhook_orders_updated(
    request: Request,
    db: Session = Depends(get_db),
    x_shopify_hmac_sha256: str = Header(None)
):
    body = await request.body()

    if not verify_webhook(x_shopify_hmac_sha256, body):
        return {"status": "error", "message": "Invalid HMAC"}

    data = json.loads(body)

    order = db.query(Order).filter_by(
        shopify_order_id=data["id"]
    ).first()

    if order:
        order.financial_status = data.get("financial_status")
        db.commit()

    return {"status": "ok"}
