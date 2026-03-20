from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy import select


from backend.models.cart import CartItem
from backend.schemas.cart import CartItemAdd
from backend.crud.cart import cart_crud
from backend.crud.product import product_crud

from backend.core.exceptions.cart_exceptions import *
from backend.core.exceptions.product_exceptions import *

class CartItemService:

    @staticmethod
    async def add_item_into_cart(
        db: AsyncSession,
        user_id: int,
        item_data: CartItemAdd
    ):
        
        product = await product_crud.get_product_by_id(db, item_data.product_id)

        if not product:
            raise ProductNotFoundError(item_data.product_id)
        
        if product.is_delete:
            raise ProductDeletedError()
        
        if product.stock < item_data.quantity:
            raise CartInsufficientStockError(product.name, product.stock)
        
        cart_item = await cart_crud.add_product_into_cart(
            db,
            user_id,
            item_data.product_id,
            item_data.quantity
        )

        await db.commit()

        result = await db.execute(
            select(CartItem)
            .options(joinedload(CartItem.product))
            .where(CartItem.id == cart_item.id)
        )

        return result.scalars().first()
    
    @staticmethod
    async def get_my_cart(
        db: AsyncSession,
        user_id: int
    ):
        items = await cart_crud.get_user_cart(db, user_id)

        total_price = sum(item.product.price * item.quantity for item in items)
        
        return {
            "items": items,
            "total_price": total_price
        }
    

    @staticmethod
    async def clear_cart(
        db: AsyncSession,
        user_id: int
    ):
        
        await cart_crud.delete_all_cart_items_by_user_id(db, user_id)
        await db.commit()

cart_service = CartItemService()