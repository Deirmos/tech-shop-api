from sqlalchemy import Integer, String, DateTime, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from sqlalchemy import Enum as SQLEnum
from typing import List

from backend.core.database import Base
from backend.core.utils.order_status_enums import OrderStatus

class Order(Base):

    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    status: Mapped[OrderStatus] = mapped_column(SQLEnum(OrderStatus))
    total_price: Mapped[float] = mapped_column(Numeric(10, 2))
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    #связи
    user: Mapped["User"] = relationship(
        "User",
        back_populates="orders"
    )

    items: Mapped[List["OrderItem"]] = relationship(
        "OrderItem",
        back_populates="order"
    )