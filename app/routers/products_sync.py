from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import requests, os

from app.database import get_db
from app.models import Product

router = APIRouter(prefix="/sync", tags=["Product Sync"])

SHOPIFY_STORE_URL = os.getenv("SHOPIFY_STORE_URL")
SHOPIFY_ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")


@router.post("/products")
def sync_products(db: Session = Depends(get_db)):
    url = f"https://{SHOPIFY_STORE_URL}/admin/api/2024-07/products.json?limit=250"

    headers = {
        "X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN
    }

    r = requests.get(url, headers=headers)
    data = r.json()

    count = 0

    for p in data["products"]:
        shopify_id = p["id"]

        product = db.query(Product).filter(Product.shopify_id == shopify_id).first()
        if not product:
            product = Product(shopify_id=shopify_id)

        product.title = p["title"]
        product.body_html = p.get("body_html")
        product.vendor = p.get("vendor")
        product.product_type = p.get("product_type")
        product.status = p.get("status")

        if p.get("image"):
            product.image = p["image"]["src"]

        if p.get("variants"):
            product.price = p["variants"][0]["price"]

        product.created_at = p.get("created_at")
        product.updated_at = p.get("updated_at")

        db.add(product)
        count += 1

    db.commit()

    return {"status": "ok", "imported": count}
