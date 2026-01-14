from pydantic import BaseModel, Field, ConfigDict
from backend.schemas.product import ProductResponse

class CartItemBase(BaseModel):
    product_id: int
    quantity: int = Field(1, gt=0)

class CartItemAdd(CartItemBase):
    pass

class CartItemResponse(BaseModel):
    id: int
    user_id: int
    product_id: int
    quantity: int

    product: ProductResponse

    model_config = ConfigDict(from_attributes=True)

class CartSummary(BaseModel):
    items: list[CartItemResponse]
    total_price: float