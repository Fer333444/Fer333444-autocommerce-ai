# app/routers/admin_products.py

from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Product

router = APIRouter(tags=["Admin Products"])

templates = Jinja2Templates(directory="templates")


@router.get("/products")
def admin_products(request: Request, db: Session = Depends(get_db)):
    products = db.query(Product).all()

    products_data = [
        {
            "id": p.id,
            "shopify_id": p.shopify_id,
            "title": p.title,
            "body_html": p.body_html,
            "vendor": p.vendor,
            "product_type": p.product_type,
            "status": p.status,
            "image": p.image,
            "price": float(p.price) if p.price else None,
            "created_at": p.created_at,
            "updated_at": p.updated_at
        }
        for p in products
    ]

    return templates.TemplateResponse(
        "admin_products.html",
        {"request": request, "products": products_data}
    )
