
from fastapi import APIRouter
from app.services.orders_service import OrderCreate, OrderPublic, create_order_demo

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/", response_model=OrderPublic)
async def create_order(order: OrderCreate):
    """
    Endpoint de ejemplo que simula crear un pedido.
    """
    return create_order_demo(order)
