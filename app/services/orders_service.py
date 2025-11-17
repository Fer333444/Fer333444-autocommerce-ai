
from datetime import datetime
from pydantic import BaseModel
from typing import List


class OrderItem(BaseModel):
    product_id: int
    quantity: int = 1


class OrderCreate(BaseModel):
    items: List[OrderItem]
    customer_email: str


class OrderPublic(BaseModel):
    id: int
    created_at: datetime
    items: List[OrderItem]
    customer_email: str
    total: float


def create_order_demo(order: OrderCreate) -> OrderPublic:
    """
    Crea un pedido de ejemplo. Calcula un total simple.
    En un proyecto real aquí llamarías a la capa de base de datos.
    """
    total = 0.0
    for item in order.items:
        total += 10.0 * item.quantity

    return OrderPublic(
        id=1,
        created_at=datetime.utcnow(),
        items=order.items,
        customer_email=order.customer_email,
        total=round(total, 2),
    )
