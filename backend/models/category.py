from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List

from backend.core.database import Base

class Category(Base):

    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True)
    slug: Mapped[str] = mapped_column(String)
    description: Mapped[Text] = mapped_column(Text, nullable=True)

    #связи
    products: Mapped[List["Product"]] = relationship(
        "Product",
        back_populates="category"
    )