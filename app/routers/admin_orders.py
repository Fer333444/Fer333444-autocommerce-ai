# app/routers/admin_orders.py

from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Order

router = APIRouter(tags=["Admin Orders"])

templates = Jinja2Templates(directory="templates")


@router.get("/orders")
def admin_orders(request: Request, db: Session = Depends(get_db)):
    orders = db.query(Order).all()

    orders_data = []
    for o in orders:
        orders_data.append({
            "id": o.id,
            "shopify_order_id": o.shopify_order_id,
            "order_number": o.order_number,
            "financial_status": o.financial_status,
            "items": [
                {
                    "title": item.title,
                    "quantity": item.quantity,
                    "price": float(item.price)
                }
                for item in o.items
            ]
        })

    return templates.TemplateResponse(
        "admin_orders.html",
        {"request": request, "orders": orders_data}
    )
