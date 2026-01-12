from sqlalchemy import Integer, String, Text, Numeric, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List

from backend.core.database import Base

class Product(Base):

    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    name: Mapped[str] = mapped_column(String, index=True)
    description: Mapped[Text] = mapped_column(Text)
    image_url: Mapped[str] = mapped_column(String, nullable=True)

    price: Mapped[float] = mapped_column(Numeric(10, 2))
    stock: Mapped[int] = mapped_column(Integer)

    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("categories.id"))

    is_delete: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    #связи
    category: Mapped["Category"] = relationship(
        "Category",
        back_populates="products"
    )

    order_items: Mapped[List["OrderItem"]] = relationship(
        "OrderItem",
        back_populates="product"
    )
