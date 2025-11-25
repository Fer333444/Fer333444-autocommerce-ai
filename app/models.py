from sqlalchemy import Column, Integer, String, Numeric, BigInteger, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class Order(Base):
    __tablename__ = "order"

    id = Column(Integer, primary_key=True, index=True)
    shopify_order_id = Column(BigInteger, index=True)
    order_number = Column(String)
    financial_status = Column(String)

    items = relationship("OrderItem", back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("order.id"))
    product_id = Column(BigInteger)
    variant_id = Column(BigInteger)
    title = Column(String)
    quantity = Column(Integer)
    price = Column(Numeric(10,2))

    order = relationship("Order", back_populates="items")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    shopify_id = Column(BigInteger, unique=True, index=True)
    title = Column(String, nullable=False)
    body_html = Column(String)
    vendor = Column(String)
    product_type = Column(String)
    status = Column(String)
    image = Column(String)
    price = Column(Numeric(10, 2))
    created_at = Column(String)
    updated_at = Column(String)
