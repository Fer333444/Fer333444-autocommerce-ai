# app/routers/admin_panel.py

from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Order, OrderItem

router = APIRouter(
    prefix="/admin",
    tags=["Admin Panel"]
)

templates = Jinja2Templates(directory="app/templates")

# ======================================================
# 🟦 Pantalla principal del admin
# ======================================================

@router.get("/orders")
def admin_orders(request: Request, db: Session = Depends(get_db)):

    # Obtener todos los pedidos
    orders = db.query(Order).all()

    # Convertir OrderItem en "productos" si quieres listarlos abajo
    # (O puedes mostrar items dentro de cada pedido)
    products = db.query(OrderItem).all()

    return templates.TemplateResponse(
        "admin_orders.html",
        {
            "request": request,
            "orders": orders,
            "products": products
        }
    )


# ======================================================
# 🟩 Vista de detalle de un pedido (opcional)
# ======================================================

@router.get("/orders/{order_id}")
def order_detail(order_id: int, request: Request, db: Session = Depends(get_db)):

    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        return {"error": "Pedido no encontrado"}

    return templates.TemplateResponse(
        "admin_order_detail.html",
        {
            "request": request,
            "order": order,
            "items": order.items  # relación ya viene desde models.py
        }
    )
