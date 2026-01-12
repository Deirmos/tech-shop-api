from pydantic import BaseModel, ConfigDict
from backend.core.utils.order_status_enums import OrderStatus
from datetime import datetime
from typing import List
from decimal import Decimal

from backend.schemas.order_item import OrderItemCreate, OrderItemResponse

class UserShortInfo(BaseModel):
    id: int
    username: str
    email: str

class OrderBase(BaseModel):
    user_id: int
    status: OrderStatus
    total_price: Decimal
    created_at: datetime

class OrderCreate(BaseModel):
    items: List[OrderItemCreate]

class OrderResponse(OrderBase):
    id: int
    items: List[OrderItemResponse]
    user: UserShortInfo

    model_config = ConfigDict(from_attributes=True)

class OrderUpdate(BaseModel):
    status: OrderStatus | None = None

