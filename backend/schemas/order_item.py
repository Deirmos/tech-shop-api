from pydantic import BaseModel, ConfigDict, Field
from decimal import Decimal

class OrderItemBase(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)

class OrderItemCreate(OrderItemBase):
    pass

class OrderItemResponse(OrderItemBase):
    id: int
    price_at_purchase: Decimal

    model_config = ConfigDict(from_attributes=True)