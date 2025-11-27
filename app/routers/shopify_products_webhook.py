# app/routers/shopify_products_webhook.py

from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Product

router = APIRouter(tags=["Shopify Products"])


@router.post("/products/update")
async def products_update(request: Request, db: Session = Depends(get_db)):
    try:
        payload = await request.json()

        shopify_id = payload.get("id")
        title = payload.get("title")
        body_html = payload.get("body_html")
        vendor = payload.get("vendor")
        product_type = payload.get("product_type")
        status = payload.get("status")
        created_at = payload.get("created_at")
        updated_at = payload.get("updated_at")

        image = None
        if payload.get("image"):
            image = payload["image"].get("src")

        product = db.query(Product).filter(Product.shopify_id == shopify_id).first()

        if product:
            # update
            product.title = title
            product.body_html = body_html
            product.vendor = vendor
            product.product_type = product_type
            product.status = status
            product.image = image
            product.updated_at = updated_at
        else:
            # create
            product = Product(
                shopify_id=shopify_id,
                title=title,
                body_html=body_html,
                vendor=vendor,
                product_type=product_type,
                status=status,
                image=image,
                created_at=created_at,
                updated_at=updated_at
            )
            db.add(product)

        db.commit()

        return {"status": "ok"}

    except Exception as e:
        print("Product webhook error:", e)
        raise HTTPException(status_code=400, detail="Invalid product webhook")
