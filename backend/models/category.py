from sqlalchemy import Integer, String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List
from sqlalchemy import text

from backend.core.database import Base

class Category(Base):

    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    name: Mapped[str] = mapped_column(String, unique=True)
    slug: Mapped[str] = mapped_column(String)

    description: Mapped[Text] = mapped_column(Text, nullable=True)
    
    is_delete: Mapped[bool] = mapped_column(Boolean, server_default=text("false"), nullable=False)

    products: Mapped[List["Product"]] = relationship(
        "Product",
        back_populates="category"
    )