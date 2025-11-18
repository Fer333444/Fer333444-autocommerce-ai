# app/main.py

from typing import Any, Dict

from fastapi import FastAPI, Request, Depends, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from .database import engine, Base, get_db
from .models import Order, OrderItem

# Crear tablas en la base de datos (si no existen)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Autocommerce AI",
    version="1.0.0",
)

# Ruta donde están tus templates en Render
templates = Jinja2Templates(directory="app/templates")


# --------------------------
#   HEALTH CHECK
# --------------------------
@app.get("/health", tags=["system"])
def health() -> Dict[str, Any]:
    return {"status": "ok"}


# --------------------------
#   HOME (REDIRIGE A ADMIN)
# --------------------------
@app.get("/", include_in_schema=False)
def root() -> RedirectResponse:
    return RedirectResponse(url="/admin/orders", status_code=status.HTTP_302_FOUND)


# --------------------------
#   WEBHOOK DE SHOPIFY
#   /api/shopify/webhooks/orders/create
# --------------------------
@app.post("/api/shopify/webhooks/orders/create", tags=["webhooks"])
async def shopify_order_created(
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Webhook de creación de pedido de Shopify.
    Guarda el pedido y sus ítems en Neon.
    """
    try:
        payload = await request.json()
    except Exception:
        return JSONResponse(
            status_code=400,
            content={"detail": "Invalid JSON"},
        )

    # --- Datos principales del pedido ---
    shopify_order_id = payload.get("id")
    order_number = payload.get("order_number") or str(payload.get("id"))
    financial_status = payload.get("financial_status") or ""

    # ¿Ya existe este pedido? (idempotencia básica)
    existing = db.query(Order).filter(Order.shopify_order_id == shopify_order_id).first()
    if existing:
        return JSONResponse(
            status_code=200,
            content={"detail": "Order already stored"},
        )

    # Crear objeto Order
    order = Order(
        shopify_order_id=shopify_order_id,
        order_number=str(order_number),
        financial_status=financial_status,
    )
    db.add(order)
    db.flush()  # para obtener order.id sin hacer commit todavía

    # --- Ítems del pedido ---
    line_items = payload.get("line_items", []) or []

    for item in line_items:
        product_id = item.get("product_id")
        variant_id = item.get("variant_id")
        title = item.get("title") or ""
        quantity = item.get("quantity") or 0
        price = item.get("price") or "0"

        order_item = OrderItem(
            order_id=order.id,
            product_id=product_id,
            variant_id=variant_id,
            title=title,
            quantity=quantity,
            price=price,
        )
        db.add(order_item)

    db.commit()

    return JSONResponse(
        status_code=200,
        content={"detail": "Order stored successfully"},
    )


# --------------------------
#   PANEL ADMIN – LISTA DE PEDIDOS
#   GET /admin/orders
# --------------------------
@app.get("/admin/orders", response_class=HTMLResponse, tags=["admin"])
def admin_orders(
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Muestra listado de pedidos guardados en Neon.
    """
    orders = db.query(Order).order_by(Order.id.desc()).all()
    return templates.TemplateResponse(
        "admin_orders.html",
        {
            "request": request,
            "orders": orders,
        },
    )


# --------------------------
#   PANEL ADMIN – DETALLE PEDIDO
#   GET /admin/orders/{order_id}
# --------------------------
@app.get("/admin/orders/{order_id}", response_class=HTMLResponse, tags=["admin"])
def admin_order_detail(
    order_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Muestra detalle de un pedido, con sus ítems.
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        return templates.TemplateResponse(
            "admin_order_detail.html",
            {
                "request": request,
                "order": None,
                "error": f"Pedido con id {order_id} no encontrado.",
            },
            status_code=404,
        )

    # gracias a relationship, order.items ya trae los OrderItem
    return templates.TemplateResponse(
        "admin_order_detail.html",
        {
            "request": request,
            "order": order,
            "items": order.items,
        },
    )
