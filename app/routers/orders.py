from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

# Modelo para recibir una orden
class Order(BaseModel):
    product_id: int
    quantity: int
    customer_email: str

@router.post("/orders")
async def create_order(order: Order):
    return {
        "message": "Orden recibida correctamente",
        "order": order
    }
