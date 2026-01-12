from sqlalchemy import Integer, String, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.core.database import Base

class OrderItem(Base):

    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(Integer, ForeignKey("orders.id"))
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"))
    quantity: Mapped[int] = mapped_column(Integer)
    price_at_purchase: Mapped[float] = mapped_column(Numeric(10, 2))

    #связи
    order: Mapped["Order"] = relationship(
        "Order",
        back_populates="items"
    )

    product: Mapped["Product"] = relationship(
        "Product",
        back_populates="order_items"
    )