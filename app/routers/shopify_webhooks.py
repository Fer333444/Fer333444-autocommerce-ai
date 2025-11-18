from fastapi import APIRouter, Request
import logging
import json

from app.database import SessionLocal
from app.models import Order, OrderItem

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/webhooks/orders/create")
async def shopify_order_create(request: Request):
    payload = await request.body()
    data = json.loads(payload.decode())

    logger.info("📦 Webhook recibido: orders/create")

    db = SessionLocal()

    try:
        # Crear pedido
        order = Order(
            shopify_order_id=data.get("id"),
            order_number=data.get("order_number"),
            financial_status=data.get("financial_status"),
        )

        db.add(order)
        db.commit()
        db.refresh(order)

        # Guardar items
        for item in data.get("line_items", []):
            order_item = OrderItem(
                order_id=order.id,
                product_id=item.get("product_id"),
                variant_id=item.get("variant_id"),
                title=item.get("title"),
                price=float(item.get("price", 0)),
                quantity=item.get("quantity", 1),
            )
            db.add(order_item)

        db.commit()
        logger.info("✅ Pedido guardado correctamente en Neon")

    except Exception as e:
        logger.error(f"❌ Error procesando webhook: {e}")
        db.rollback()

    finally:
        db.close()

    return {"status": "ok"}
