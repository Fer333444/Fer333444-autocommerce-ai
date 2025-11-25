from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Pedido, Producto
import requests
import os
from datetime import datetime

router = APIRouter(
    prefix="/admin",
    tags=["Admin Panel"]
)

# ---------------------------------------------------------
#  VARIABLES DE ENTORNO PARA SHOPIFY Y AMAZON
# ---------------------------------------------------------
SHOPIFY_STORE_URL = os.getenv("SHOPIFY_STORE_URL")
SHOPIFY_ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")
AMAZON_API_STATUS_URL = os.getenv("AMAZON_API_STATUS_URL")  # (opcional)


# ---------------------------------------------------------
#  FUNCIÓN PARA OBTENER PRODUCTOS DESDE SHOPIFY
# ---------------------------------------------------------
def obtener_productos_shopify():
    try:
        url = f"https://{SHOPIFY_STORE_URL}/admin/api/2024-07/products.json"
        headers = {"X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN}
        response = requests.get(url, headers=headers)
        return response.json().get("products", [])
    except:
        return []


# ---------------------------------------------------------
#  FUNCIÓN PARA OBTENER ESTADO AMAZON SP-API
# ---------------------------------------------------------
def obtener_estado_amazon():
    try:
        if not AMAZON_API_STATUS_URL:
            return {"status": "unknown", "detail": "No status URL"}
        r = requests.get(AMAZON_API_STATUS_URL)
        return r.json()
    except:
        return {"status": "error", "detail": "Amazon SP-API desconectado"}


# ---------------------------------------------------------
#  PLANTILLA HTML – PANEL ADMIN
# ---------------------------------------------------------
def render_panel_html(pedidos, productos, amazon_status):
    html = f"""
    <html>
    <head>
        <title>Panel Admin – Autocommerce AI</title>
        <link rel="stylesheet"
              href="https://cdn.datatables.net/1.13.1/css/jquery.dataTables.min.css" />
        <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
        <script src="https://cdn.datatables.net/1.13.1/js/jquery.dataTables.min.js"></script>
        <style>
            body {{
                font-family: Arial;
                margin: 40px;
            }}
            .card {{
                padding: 20px;
                background: #f5f5f5;
                border-radius: 10px;
                margin-bottom: 30px;
            }}
        </style>
    </head>

    <body>

        <h1>🧠 Autocommerce AI – Panel Admin</h1>
        <p>Control completo de pedidos, Shopify, Amazon y sincronización.</p>

        <div class="card">
            <h2>⭐ Estado de APIs</h2>
            <p><b>Shopify:</b> Conectado</p>
            <p><b>Amazon SP-API:</b> {amazon_status}</p>
        </div>

        <div class="card">
            <h2>📦 Pedidos Recibidos</h2>
            <table id="pedidos" class="display">
                <thead>
                    <tr>
                        <th>ID</th><th>Email</th><th>Tipo</th>
                        <th>Total</th><th>Fecha</th>
                    </tr>
                </thead>
                <tbody>
    """

    # Inyectamos los pedidos
    for p in pedidos:
        html += f"""
            <tr>
                <td>{p.id}</td>
                <td>{p.email}</td>
                <td>{p.tipo_compra}</td>
                <td>{p.total}</td>
                <td>{p.fecha}</td>
            </tr>
        """

    html += """
                </tbody>
            </table>
        </div>

        <div class="card">
            <h2>🛒 Productos en Shopify</h2>
            <table id="productos" class="display">
                <thead>
                    <tr>
                        <th>ID</th><th>Título</th><th>Precio</th><th>Stock</th>
                    </tr>
                </thead>
                <tbody>
    """

    # Productos Shopify
    for prod in productos:
        precio = prod["variants"][0]["price"] if prod.get("variants") else "-"
        stock = prod["variants"][0]["inventory_quantity"] if prod.get("variants") else "-"
        html += f"""
            <tr>
                <td>{prod["id"]}</td>
                <td>{prod["title"]}</td>
                <td>{precio}</td>
                <td>{stock}</td>
            </tr>
        """

    html += """
                </tbody>
            </table>
        </div>

        <script>
            $(document).ready(function(){
                $('#pedidos').DataTable();
                $('#productos').DataTable();
            });
        </script>

    </body>
    </html>
    """

    return html


# ---------------------------------------------------------
#  ENDPOINT PRINCIPAL DEL PANEL ADMIN
# ---------------------------------------------------------
@router.get("/orders", response_class=HTMLResponse)
def admin_orders(request: Request, db: Session = Depends(get_db)):

    pedidos = db.query(Pedido).order_by(Pedido.fecha.desc()).all()
    productos = obtener_productos_shopify()
    amazon_status = obtener_estado_amazon()

    return render_panel_html(pedidos, productos, amazon_status)
