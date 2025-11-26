# app/routers/orders.py

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Order as DBOrder, OrderItem as DBOrderItem

router = APIRouter(prefix="/orders", tags=["Orders"])


# Modelo Pydantic RENOMBRADO para no chocar con el modelo SQLAlchemy Order
class CreateOrder(BaseModel):
    product_id: int
    quantity: int
    customer_email: str


@router.post("/")
async def create_order(order: CreateOrder, db: Session = Depends(get_db)):
    """
    Ruta de ejemplo para crear órdenes manuales.
    (No afecta a Shopify ni a los webhooks)
    """

    new_order = DBOrder(
        shopify_order_id=None,
        order_number="manual",
        financial_status="pending"
    )

    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    new_item = DBOrderItem(
        order_id=new_order.id,
        product_id=order.product_id,
        variant_id=0,
        title="Manual order",
        quantity=order.quantity,
        price=0.00
    )

    db.add(new_item)
    db.commit()

    return {
        "message": "Orden creada manualmente",
        "order_id": new_order.id
    }
