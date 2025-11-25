from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Order, OrderItem

router = APIRouter(prefix="/admin", tags=["Admin Panel"])

templates = Jinja2Templates(directory="app/templates")

@router.get("/orders")
def admin_orders(request: Request, db: Session = Depends(get_db)):
    orders = db.query(Order).all()
    return templates.TemplateResponse(
        "admin_orders.html",
        {"request": request, "orders": orders}
    )

@router.get("/orders/{order_id}")
def admin_order_detail(order_id: int, request: Request, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        return {"error": "Order not found"}

    return templates.TemplateResponse(
        "admin_order_detail.html",
        {"request": request, "order": order}
    )
