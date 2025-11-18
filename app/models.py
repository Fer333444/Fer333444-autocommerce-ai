from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Order(Base):
    __tablename__ = "order"

    id = Column(Integer, primary_key=True, index=True)
    shopify_order_id = Column(String, index=True)
    order_number = Column(String)
    financial_status = Column(String)

    items = relationship("OrderItem", back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("order.id"))
    product_id = Column(String)
    variant_id = Column(String)
    title = Column(String)
    price = Column(Float)
    quantity = Column(Integer)

    order = relationship("Order", back_populates="items")
