from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime


# -----------------------------
# CUSTOMER TABLE
# -----------------------------
class Customer(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    shopify_customer_id: str = Field(index=True)
    email: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    phone: Optional[str]
    created_at: datetime = Field(default_factory=datetime.utcnow)

    orders: List["Order"] = Relationship(back_populates="customer")


# -----------------------------
# ORDER TABLE
# -----------------------------
class Order(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    shopify_order_id: str = Field(index=True)
    order_number: Optional[str]
    financial_status: Optional[str]
    fulfillment_status: Optional[str]
    total_price: Optional[str]
    currency: Optional[str]
    created_at: datetime = Field(default_factory=datetime.utcnow)

    customer_id: Optional[int] = Field(default=None, foreign_key="customer.id")
    customer: Optional[Customer] = Relationship(back_populates="orders")

    items: List["OrderItem"] = Relationship(back_populates="order")


# -----------------------------
# ORDER ITEMS TABLE
# -----------------------------
class OrderItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="order.id")
    product_id: Optional[str]
    product_title: Optional[str]
    quantity: Optional[int]
    price: Optional[str]

    order: Order = Relationship(back_populates="items")


# -----------------------------
# RAW WEBHOOK LOGS (NO MODIFICAR)
# -----------------------------
class RawWebhook(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    topic: str
    payload: str
    received_at: datetime = Field(default_factory=datetime.utcnow)
