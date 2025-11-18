from fastapi import APIRouter, Depends, Request, Query
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional, List

from database import get_session  # O el módulo donde tengas tu get_session
from models import Order, OrderItem  # Ajusta al nombre real de tus modelos

router = APIRouter()

# Carpeta de templates (la creamos en el siguiente paso)
templates = Jinja2Templates(directory="templates")


@router.get("/orders")
def admin_orders(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_session),
):
    """
    Lista de pedidos con paginación, filtro por estado y búsqueda.
    """
    query = db.query(Order)

    # Filtro por estado (financial_status)
    if status:
        query = query.filter(Order.financial_status == status)

    # Búsqueda por número de pedido o id de Shopify
    if search:
        like = f"%{search}%"
        query = query.filter(
            (Order.order_number.ilike(like)) |
            (Order.shopify_order_id.ilike(like))
        )

    total = query.count()
    orders = (
        query
        .order_by(Order.created_at.desc())  # si tienes created_at, si no, quita esto
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    total_pages = (total + page_size - 1) // page_size if total > 0 else 1

    return templates.TemplateResponse(
        "admin_orders.html",
        {
            "request": request,
            "orders": orders,
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": total_pages,
            "status": status,
            "search": search,
        },
    )


@router.get("/orders/{order_id}")
def admin_order_detail(
    order_id: int,
    request: Request,
    db: Session = Depends(get_session),
):
    """
    Detalle de un pedido: datos generales + productos.
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        # Podríamos devolver 404, pero para el panel es cómodo mostrar página vacía
        return templates.TemplateResponse(
            "admin_order_detail.html",
            {"request": request, "order": None, "items": []},
        )

    # Carga de items (ajusta a tu relación real)
    items: List[OrderItem] = (
        db.query(OrderItem)
        .filter(OrderItem.order_id == order.id)
        .all()
    )

    return templates.TemplateResponse(
        "admin_order_detail.html",
        {
            "request": request,
            "order": order,
            "items": items,
        },
    )
