# app/models.py

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
