from fastapi import APIRouter, Request, Header, Depends
from sqlalchemy.orm import Session
import hmac, hashlib, base64, json, os

from app.database import get_db
from app.models import Product

router = APIRouter(prefix="/shopify/webhook", tags=["Shopify Webhooks"])

SHOPIFY_API_SECRET = os.getenv("SHOPIFY_API_SECRET")


def verify_hmac(hmac_header: str, body: bytes) -> bool:
    digest = hmac.new(
        SHOPIFY_API_SECRET.encode("utf-8"),
        body,
        hashlib.sha256
    ).digest()

    expected_hmac = base64.b64encode(digest).decode()
    return hmac.compare_digest(expected_hmac, hmac_header)


@router.post("/products/update")
async def webhook_products_update(
    request: Request,
    db: Session = Depends(get_db),
    x_shopify_hmac_sha256: str = Header(None)
):
    body = await request.body()

    if not verify_hmac(x_shopify_hmac_sha256, body):
        return {"status": "error", "message": "Invalid HMAC"}

    data = json.loads(body)

    shopify_id = data["id"]
    product = db.query(Product).filter(Product.shopify_id == shopify_id).first()
    if not product:
        product = Product(shopify_id=shopify_id)

    product.title = data["title"]
    product.body_html = data.get("body_html")
    product.vendor = data.get("vendor")
    product.product_type = data.get("product_type")
    product.status = data.get("status")

    if data.get("image"):
        product.image = data["image"]["src"]

    if data.get("variants"):
        product.price = data["variants"][0]["price"]

    product.created_at = data.get("created_at")
    product.updated_at = data.get("updated_at")

    db.add(product)
    db.commit()

    print("PRODUCTO GUARDADO/ACTUALIZADO:", shopify_id)

    return {"status": "ok", "shopify_id": shopify_id}
