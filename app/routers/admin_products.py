from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import os

from app.database import get_db
from app.models import Product

router = APIRouter(prefix="/admin", tags=["Admin Products"])

templates = Jinja2Templates(directory="app/templates")


@router.get("/products")
def admin_products(request: Request, db: Session = Depends(get_db)):
    products = db.query(Product).all()
    return templates.TemplateResponse(
        "admin_products.html",
        {
            "request": request,
            "products": products,
            "shopify_domain": os.getenv("SHOPIFY_STORE_URL")
        }
    )
