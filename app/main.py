from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
import uvicorn
from database import SessionLocal, engine, Base
from models import Order, OrderItem
import json

# Crear tablas en Neon (si no existen)
Base.metadata.create_all(bind=engine)

app = FastAPI()

# -------------------------------
# Página de prueba en "/"
# -------------------------------
@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <h1>🚀 AutoCommerce AI – Shopify Webhooks</h1>
    <p>El servidor está funcionando correctamente.</p>
    """


# -------------------------------
# Webhook Shopify → Creación pedido
# -------------------------------
@app.post("/api/shopify/webhooks/orders/create")
async def shopify_order_created(request: Request):
    db = SessionLocal()

    try:
        data = await request.json()
        print("📦 Webhook recibido:", json.dumps(data, indent=2))

        shopify_order_id = str(data["id"])
        order_number = str(data.get("order_number", ""))
        financial_status = data.get("financial_status", "")

        # Guardar orden
        new_order = Order(
            shopify_order_id=shopify_order_id,
            order_number=order_number,
            financial_status=financial_status
        )
        db.add(new_order)
        db.commit()
        db.refresh(new_order)

        # Guardar items
        for item in data.get("line_items", []):
            order_item = OrderItem(
                order_id=new_order.id,
                product_id=item.get("product_id"),
                variant_id=item.get("variant_id"),
                title=item.get("title"),
                quantity=item.get("quantity", 0),
                price=float(item.get("price", 0))
            )
            db.add(order_item)

        db.commit()

        print("✅ Pedido guardado correctamente")
        return {"status": "success"}

    except Exception as e:
        print("❌ ERROR en webhook:", str(e))
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        db.close()


# -------------------------------
# Webhook Shopify → Actualización pedido
# -------------------------------
@app.post("/api/shopify/webhooks/orders/updated")
async def shopify_order_updated(request: Request):
    db = SessionLocal()

    try:
        data = await request.json()
        print("♻ Webhook actualización pedido:", json.dumps(data, indent=2))

        shopify_order_id = str(data["id"])
        new_status = data.get("financial_status", "")

        order = db.query(Order).filter(
            Order.shopify_order_id == shopify_order_id
        ).first()

        if order:
            order.financial_status = new_status
            db.commit()
            print("✅ Orden actualizada")
        else:
            print("⚠ No existe la orden, ignorado.")

        return {"status": "updated"}

    except Exception as e:
        print("❌ ERROR update:", str(e))
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        db.close()


# -------------------------------
# Webhook Shopify → Pago realizado
# -------------------------------
@app.post("/api/shopify/webhooks/payments/update")
async def shopify_payment_update(request: Request):
    try:
        data = await request.json()
        print("💳 Webhook pago recibido:", json.dumps(data, indent=2))
        return {"status": "payment_received"}

    except Exception as e:
        print("❌ ERROR pago:", str(e))
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------
# Webhook Shopify → Inventario
# -------------------------------
@app.post("/api/shopify/webhooks/inventory/update")
async def shopify_inventory_update(request: Request):
    try:
        data = await request.json()
        print("📦 Webhook inventario recibido:", json.dumps(data, indent=2))
        return {"status": "inventory_updated"}

    except Exception as e:
        print("❌ ERROR inventario:", str(e))
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------
# Iniciar localmente
# -------------------------------
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080)
	