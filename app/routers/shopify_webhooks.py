from fastapi import APIRouter, Request, Header, HTTPException, Depends
import hmac
import hashlib
import base64
import json
from sqlmodel import Session
from app.database import get_session
from app.models import Customer, Order, OrderItem, RawWebhook
import os

router = APIRouter()

SHOPIFY_WEBHOOK_SECRET = os.getenv("SHOPIFY_WEBHOOK_SECRET")

if not SHOPIFY_WEBHOOK_SECRET:
    raise Exception("❌ ERROR: Falta SHOPIFY_WEBHOOK_SECRET en variables de entorno")


def verify_webhook(body: bytes, hmac_header: str) -> bool:
    """Verifica que Shopify envía el webhook correcto usando HMAC-SHA256."""

    computed_hmac = base64.b64encode(
        hmac.new(
            SHOPIFY_WEBHOOK_SECRET.encode("utf-8"),
            body,
            hashlib.sha256
        ).digest()
    ).decode()

    return hmac.compare_digest(computed_hmac, hmac_header)


# ============================================================
# 🛒 WEBHOOK: orders/create
# ============================================================
@router.post("/webhooks/orders/create")
async def orders_create(
    request: Request,
    x_shopify_hmac_sha256: str = Header(None),
    session: Session = Depends(get_session)
):

    body = await request.body()

    # 1. Validar firma HMAC
    if not verify_webhook(body, x_shopify_hmac_sha256):
        raise HTTPException(status_code=401, detail="Invalid HMAC signature")

    data = json.loads(body.decode())

    # 2. Registrar RAW webhook
    raw = RawWebhook(
        topic="orders/create",
        payload=json.dumps(data)
    )
    session.add(raw)
    session.commit()

    print("📥 Recibido webhook de creación de pedido")

    # 3. Registrar cliente
    customer_data = data.get("customer", {})

    customer = Customer(
        shopify_customer_id=str(customer_data.get("id")),
        email=customer_data.get("email"),
        first_name=customer_data.get("first_name"),
        last_name=customer_data.get("last_name"),
        phone=customer_data.get("phone"),
    )
    session.add(customer)
    session.commit()

    # 4. Registrar pedido
    order = Order(
        shopify_order_id=str(data.get("id")),
        order_number=str(data.get("order_number")),
        financial_status=data.get("financial_status"),
        fulfillment_status=data.get("fulfillment_status"),
        total_price=data.get("total_price"),
        currency=data.get("currency"),
        customer_id=customer.id,
    )
    session.add(order)
    session.commit()

    # 5. Registrar items del pedido
    line_items = data.get("line_items", [])

    for item in line_items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=str(item.get("product_id")),
            product_title=item.get("title"),
            quantity=item.get("quantity"),
            price=item.get("price"),
        )
        session.add(order_item)

    session.commit()

    print("🛒 Pedido guardado correctamente en la base de datos Neon.")

    return {"status": "success"}


# ============================================================
# 📦 WEBHOOK: products/update
# ============================================================
@router.post("/webhooks/products/update")
async def products_update(
    request: Request,
    x_shopify_hmac_sha256: str = Header(None),
    session: Session = Depends(get_session)
):

    body = await request.body()

    # Validar firma
    if not verify_webhook(body, x_shopify_hmac_sha256):
        raise HTTPException(status_code=401, detail="Invalid HMAC signature")

    data = json.loads(body.decode())

    # Guardar RAW
    raw = RawWebhook(
        topic="products/update",
        payload=json.dumps(data)
    )
    session.add(raw)
    session.commit()

    print("📦 Producto actualizado recibido y guardado en RAW.")

    return {"status": "success"}
