from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from backend.schemas.order import OrderCreate, OrderResponse
from backend.core.utils.order_status_enums import OrderStatus
from backend.services.order_service import order_service
from backend.models.user import User
from backend.core.database import get_db
from backend.services.user_service import get_current_admin_user, get_current_user

router = APIRouter(prefix="/order", tags=["orders"])

admin_router = APIRouter(prefix="/admin/order", tags=["admin-orders"])

@router.get("/history", response_model=List[OrderResponse])
async def get_orders_history(
    status: Optional[OrderStatus] = None,
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    
    orders_history = await order_service.get_user_orders_history(
        db,
        current_user=current_user,
        status=status,
        skip=skip,
        limit=limit
    )

    return orders_history

@router.post("/", response_model=OrderResponse)
async def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    
    order = await order_service.create_order(db, order_data, current_user.id)

    return order

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order_by_id(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    
    order = await order_service.get_one_order_by_id(db, order_id, current_user)

    return order

@admin_router.put("/status/{order_id}", response_model=OrderResponse)
async def edit_order_status_by_id(
    order_id: int,
    new_status: OrderStatus,
    user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    
    order = await order_service.edit_one_order_status_by_id(db, order_id, new_status)

    return OrderResponse.model_validate(order, from_attributes=True)

@admin_router.get("/all", response_model=List[OrderResponse])
async def get_all_orders_admin(
    user_id: Optional[int] = None,
    status: Optional[OrderStatus] = None,
    skip: int = 0,
    limit: int = 10,
    admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    
    orders = await order_service.get_all_orders_for_admin(
        db,
        user_id,
        status,
        skip,
        limit
    )

    return orders

@router.post("/checkout", response_model=OrderResponse)
async def checkout_cart(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    
    return await order_service.create_order_from_cart(
        db,
        user_id=current_user.id,
        email=current_user.email,
        background_tasks=background_tasks
    )

