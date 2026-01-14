from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from typing import Optional, List

from backend.crud.order import order_crud
from backend.crud.product import product_crud
from backend.schemas.order import OrderCreate, OrderUpdate
from backend.models.order_item import OrderItem
from backend.models.user import User
from backend.core.utils.order_status_enums import OrderStatus

from backend.crud.cart import cart_crud
from backend.models.order import Order

class OrderService:

    @staticmethod
    async def create_order(
        db: AsyncSession,
        order_data: OrderCreate,
        user_id: int
    ):
        total_price = 0
        order_items = []
        try: 
            for item in order_data.items:
                product = await product_crud.get_product_by_id(db, item.product_id)

                if not product:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Товар {item.product_id} не найден"
                    )
                
                if product.stock < item.quantity:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Недостаточно товара {product.name} на складе"
                    )
            
                total_price += product.price * item.quantity
                product.stock -= item.quantity

                order_items.append(OrderItem(
                    product_id=product.id,
                    quantity=item.quantity,
                    price_at_purchase=product.price
                ))

            new_order = await order_crud._create_order_record(
                db,
                user_id=user_id,
                total_price=total_price,
                items=order_items
            )

            await db.commit()
            await db.refresh(new_order, attribute_names=["items"])

            return new_order
        
        except Exception as e:
            await db.rollback()
            raise e

    @staticmethod
    async def get_one_order_by_id(
        db: AsyncSession,
        order_id: int,
        current_user: User
    ):
        
        order = await order_crud.get_oder_by_id(db, order_id)

        if order is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Заказа под ID({order_id}) не найдено"
            )
        
        if not current_user.is_admin and order.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="У вас недостаточно прав"
            )
        
        return order
    
    @staticmethod
    async def get_all_orders_for_admin(
        db: AsyncSession,
        user_id: Optional[int] = None,
        status: Optional[OrderStatus] = None,
        skip: int = 0,
        limit: int = 10
    ):
        
        return await order_crud.get_multi_orders(
            db,
            user_id=user_id,
            status=status,
            skip=skip,
            limit=limit
        )
    
    @staticmethod
    async def edit_one_order_status_by_id(
        db: AsyncSession,
        order_id: int,
        new_status: OrderStatus
    ):
        
        order = await order_crud.get_oder_by_id(db, order_id)

        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Заказа под ID({order_id}) не найдено"
            )
        
        old_status = order.status
        
        if order.status == OrderStatus.SHIPPED and new_status == OrderStatus.CANCELLED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Нельзя отменить заказ, который уже доставляется"
            )
        
        if order.status == OrderStatus.COMPLETED and new_status != OrderStatus.COMPLETED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Нельзя изменить статус законченного заказа"
            )
        
        if order.status == OrderStatus.SHIPPED and new_status != OrderStatus.COMPLETED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Нельзя изменить статус товара в доставке на что-то, кроме 'Доставлен'"
            )

        if order.status == OrderStatus.CANCELLED and new_status != OrderStatus.CANCELLED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Нельзя изменить статус отмененного заказа"
            )
        
        if new_status == OrderStatus.CANCELLED and old_status != OrderStatus.CANCELLED:
            for item in order.items:
                product = await product_crud.get_product_by_id(db, item.product_id)
                if product:
                    product.stock += item.quantity

        updated_order = await order_crud.edit_order_status_by_id(db, order_id, new_status)

        await db.commit()
        await db.refresh(updated_order)

        return updated_order
    
    @staticmethod
    async def get_user_orders_history(
        db: AsyncSession,
        current_user: User,
        status: Optional[OrderStatus] = None,
        skip: int = 0,
        limit: int = 10
    ):
        return await order_crud.get_multi_orders(
            db,
            user_id=current_user.id,
            status=status,
            skip=skip,
            limit=limit
        )
    
    @staticmethod
    async def create_order_from_cart(
        db: AsyncSession,
        user_id: int
    ):
        cart_items = await cart_crud.get_user_cart(db, user_id)

        if not cart_items:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ваша корзина пуста. Нечего оформлять!"
            )
        
        total_price = 0
        order_items_to_create = []

        try:
            for cart_item in cart_items:
                product = cart_item.product

                if product.stock < cart_item.quantity:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Недостаточно товара {product.name} на складе(доступно: {product.stock})"
                    )
                
                total_price += product.price * cart_item.quantity

                product.stock -= cart_item.quantity

                order_items_to_create.append(OrderItem(
                    product_id=product.id,
                    quantity=cart_item.quantity,
                    price_at_purchase=product.price
                ))

            new_order = await order_crud._create_order_record(
                db,
                user_id,
                total_price,
                order_items_to_create
            )

            await cart_crud.delete_all_cart_items_by_user_id(db, user_id)

            await db.commit()
            await db.refresh(new_order, attribute_names=["items"])

            return new_order
        
        except Exception as e:
            await db.rollback()
            raise e
    
order_service = OrderService()