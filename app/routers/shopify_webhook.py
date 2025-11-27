# app/routers/shopify_webhook.py

from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Order, OrderItem

router = APIRouter(tags=["Shopify Orders"])


@router.post("/orders/create")
async def shopify_orders(request: Request, db: Session = Depends(get_db)):
    try:
        payload = await request.json()

        shopify_order_id = payload.get("id")
        order_number = payload.get("order_number")
        financial_status = payload.get("financial_status")
        line_items = payload.get("line_items", [])

        order = Order(
            shopify_order_id=shopify_order_id,
            order_number=order_number,
            financial_status=financial_status
        )
        db.add(order)
        db.commit()
        db.refresh(order)

        for item in line_items:
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

        return {"status": "ok"}

    except Exception as e:
        print("Webhook Error:", e)
        raise HTTPException(status_code=400, detail="Invalid Webhook")
