
from pydantic import BaseModel
from typing import List


class Product(BaseModel):
    id: int
    name: str
    price: float
    currency: str = "USD"


def get_demo_products() -> List[Product]:
    """
    Devuelve una lista fija de productos de ejemplo.
    No usa base de datos, así que funciona en cualquier entorno.
    """
    return [
        Product(id=1, name="Camiseta básica", price=19.99),
        Product(id=2, name="Taza AutoCommerce AI", price=9.99),
        Product(id=3, name="Gorra edición limitada", price=24.99),
    ]
