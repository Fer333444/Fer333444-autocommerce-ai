from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.database import get_db, Base, engine
from app.models import Order, OrderItem

import uvicorn

# Crear tablas si no existen
Base.metadata.create_all(bind=engine)

# App
app = FastAPI()

# Templates (para /admin/orders)
templates = Jinja2Templates(directory="app/templates")


# -------------------------------------------------------------
# HEALTH CHECK
# -------------------------------------------------------------
@app.get("/")
def health():
    return {"status": "OK", "message": "Server running"}


# -------------------------------------------------------------
# WEBHOOK SHOPIFY - ORDER CREATE
# -------------------------------------------------------------
@app.post("/api/shopify/webhooks/orders/create")
async def shopify_order_create(request: Request, db: Session = Depends(get_db)):
    try:
        data = await request.json()

        shopify_order_id = data.get("id")
        order_number = data.get("order_number")
        financial_status = data.get("financial_status", "unknown")
        total_price = data.get("total_price", "0.00")

        # Guardar el pedido principal
        order = Order(
            shopify_order_id=shopify_order_id,
            order_number=str(order_number),
            financial_status=financial_status,
            total_price=total_price
        )
        db.add(order)
        db.commit()
        db.refresh(order)

        # Guardar items
        for item in data.get("line_items", []):
            order_item = OrderItem(
                order_id=order.id,
                product_id=item.get("product_id"),
                variant_id=item.get("variant_id"),
                title=item.get("title"),
                quantity=item.get("quantity"),
                price=item.get("price")
            )
            db.add(order_item)

        db.commit()

        return JSONResponse({"success": True})

    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=400)


# -------------------------------------------------------------
# WEBHOOK SHOPIFY - ORDER UPDATE
# -------------------------------------------------------------
@app.post("/api/shopify/webhooks/orders/updated")
async def shopify_order_updated(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    shopify_order_id = data.get("id")

    order = db.query(Order).filter(Order.shopify_order_id == shopify_order_id).first()
    if not order:
        return {"status": "ignored", "message": "Order not found"}

    order.financial_status = data.get("financial_status", order.financial_status)
    order.total_price = data.get("total_price", order.total_price)

    db.commit()

    return {"success": True}


# -------------------------------------------------------------
# WEBHOOK SHOPIFY - ORDER DELETE
# -------------------------------------------------------------
@app.post("/api/shopify/webhooks/orders/delete")
async def shopify_order_delete(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    shopify_order_id = data.get("id")

    order = db.query(Order).filter(Order.shopify_order_id == shopify_order_id).first()
    if not order:
        return {"ignored": True}

    db.delete(order)
    db.commit()

    return {"success": True}


# -------------------------------------------------------------
# PÁGINA ADMIN - LISTA DE PEDIDOS
# -------------------------------------------------------------
@app.get("/admin/orders")
def admin_orders(request: Request, db: Session = Depends(get_db)):
    orders = db.query(Order).all()

    enriched_orders = []
    for order in orders:
        items = (
            db.query(OrderItem)
            .filter(OrderItem.order_id == order.id)
            .all()
        )

        enriched_orders.append({
            "id": order.id,
            "shopify_order_id": order.shopify_order_id,
            "order_number": order.order_number,
            "financial_status": order.financial_status,
            "created_at": order.created_at,
            "total_price": order.total_price,
            "items": items
        })

    return templates.TemplateResponse(
        "admin_orders.html",
        {"request": request, "orders": enriched_orders}
    )


# -------------------------------------------------------------
# EJECUCIÓN LOCAL
# -------------------------------------------------------------
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
