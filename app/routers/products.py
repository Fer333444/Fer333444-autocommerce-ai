
from fastapi import APIRouter
from typing import List

from app.services.products_service import Product, get_demo_products

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/", response_model=List[Product])
async def list_products():
    return get_demo_products()


@router.get("/{product_id}", response_model=Product)
async def get_product(product_id: int):
    products = get_demo_products()
    for p in products:
        if p.id == product_id:
            return p
    return products[0]
