from sqlalchemy import Integer, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, TYPE_CHECKING

from backend.core.database import Base

if TYPE_CHECKING:
    from backend.models.order import Order
    from backend.models.cart import CartItem

class User(Base):
    
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    username: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)

    #связи
    orders: Mapped[List["Order"]] = relationship(
        "Order",
        back_populates="user"
    )

    cart_items: Mapped[List["CartItem"]] = relationship(
        "CartItem",
        back_populates="user",
        cascade="all, delete-orphan"
    )