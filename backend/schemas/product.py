from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from decimal import Decimal

class ProductBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., min_length=3, max_length=1050)
    price: Decimal
    stock: int = Field(..., ge=0)

class ProductCreate(ProductBase):
    category_id: int

class ProductResponse(ProductBase):
    id: int
    category_id: int
    is_delete: bool
    image_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class ProductEdit(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = Field(None, min_length=3, max_length=1050)
    price: Optional[Decimal] = None
    stock: Optional[int] = None
