from fastapi import FastAPI, Request, Depends
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pydantic import BaseModel
import json

from database import SessionLocal, engine, Base
from models import Order, OrderItem

# Crear tablas si no existen
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Conectar templates
templates = Jinja2Templates(directory="templates")

# Dependency para DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ----------------------------
#   MODELO PARA VALIDAR WEBHOOK
# ----------------------------
class ShopifyOrder(BaseModel):
    id: int
    order_number: int
    financial_status: str
    line_items: list


# ----------------------------
#   RUTA PRINCIPAL
# ----------------------------
@app.get("/")
def home():
    return {"message": "AutoCommerce AI funcionando correctamente 🚀"}


# ----------------------------
#   WEBHOOK: ORDER CREATE
# ----------------------------
@app.post("/api/shopify/webhooks/orders/create")
async def shopify_order_create(request: Request, db: Session = Depends(get_db)):
    body = await request.json()

    shopify_id = body.get("id")
    order_number = body.get("order_number")
    financial_status = body.get("financial_status", "unknown")
    line_items = body.get("line_items", [])

    # Guardar pedido
    new_order = Order(
        shopify_order_id=str(shopify_id),
        order_number=str(order_number),
        financial_status=financial_status
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    # Guardar items
    for item in line_items:
        db_item = OrderItem(
            order_id=new_order.id,
            product_id=item.get("product_id"),
            variant_id=item.get("variant_id"),
            title=item.get("title"),
            quantity=item.get("quantity"),
            price=item.get("price")
        )
        db.add(db_item)

    db.commit()
    return JSONResponse({"status": "order_saved"})


# ----------------------------
#   WEBHOOK: ORDER UPDATE
# ----------------------------
@app.post("/api/shopify/webhooks/orders/update")
async def shopify_order_update(request: Request, db: Session = Depends(get_db)):
    body = await request.json()

    shopify_id = body.get("id")
    financial_status = body.get("financial_status")

    order = db.query(Order).filter(Order.shopify_order_id == str(shopify_id)).first()

    if order:
        order.financial_status = financial_status
        db.commit()

    return JSONResponse({"status": "order_updated"})


# ----------------------------
#   WEBHOOK: REFUND CREATE
# ----------------------------
@app.post("/api/shopify/webhooks/refunds/create")
async def shopify_refund_create(request: Request, db: Session = Depends(get_db)):
    body = await request.json()
    shopify_id = body.get("order_id")

    order = db.query(Order).filter(Order.shopify_order_id == str(shopify_id)).first()

    if order:
        order.financial_status = "refunded"
        db.commit()

    return JSONResponse({"status": "refund_saved"})


# ----------------------------
#   PANEL ADMIN: LISTA DE ÓRDENES
# ----------------------------
@app.get("/admin/orders", response_class=HTMLResponse)
def admin_orders(request: Request, db: Session = Depends(get_db)):
    orders = db.query(Order).order_by(Order.id.desc()).all()
    return templates.TemplateResponse(
        "admin_orders.html",
        {"request": request, "orders": orders}
    )


# ----------------------------
#   PANEL ADMIN: DETALLE DE UNA ORDEN
# ----------------------------
@app.get("/admin/orders/{order_id}", response_class=HTMLResponse)
def admin_order_detail(order_id: int, request: Request, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    items = db.query(OrderItem).filter(OrderItem.order_id == order_id).all()

    return templates.TemplateResponse(
        "admin_order_detail.html",
        {"request": request, "order": order, "items": items}
    )
