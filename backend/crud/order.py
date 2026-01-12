from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload
from decimal import Decimal
from typing import Optional, List

from backend.models.order import Order
from backend.schemas.order import OrderCreate, OrderUpdate
from backend.core.utils.order_status_enums import OrderStatus

class OrderCRUD:

    @staticmethod
    async def get_oder_by_id(
        db: AsyncSession,
        order_id: int
    ) -> Order | None:
        
        order = await db.execute(select(Order).where(Order.id == order_id).options(selectinload(Order.items)))

        return order.scalar_one_or_none()
    
    @staticmethod
    async def _create_order_record(db: AsyncSession, user_id: int, total_price: Decimal, items: list) -> Order:
        order = Order(
            user_id=user_id,
            total_price=total_price,
            status=OrderStatus.NEW,
            items=items
        )
        
        db.add(order)
        await db.flush()

        return order
    
    @staticmethod
    async def edit_order_status_by_id(
        db: AsyncSession,
        order_id: int,
        new_status: OrderStatus
    ) -> Order | None:
        
        order = await OrderCRUD.get_oder_by_id(db, order_id)

        if not order:
            return None
        
        order.status = new_status

        await db.flush()
        await db.refresh(order)
        
        return order
    
    @staticmethod
    async def get_multi_orders(
        db: AsyncSession,
        user_id: Optional[int] = None,
        status: Optional[OrderStatus] = None,
        skip: int = 0,
        limit: int = 10
    ) -> List[Order]:
        
        query = select(Order).options(
            selectinload(Order.items),
            joinedload(Order.user)
            )

        if user_id is not None:
            query = query.where(Order.user_id == user_id)

        if status is not None:
            query = query.where(Order.status == status)

        query = query.offset(skip).limit(limit).order_by(Order.id.desc())

        result = await db.execute(query)

        return result.scalars().all()



order_crud = OrderCRUD()