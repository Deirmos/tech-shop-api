from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from sqlalchemy.orm import joinedload
from sqlalchemy import select


from backend.models.cart import CartItem
from backend.schemas.cart import CartItemAdd
from backend.crud.cart import cart_crud
from backend.crud.product import product_crud

class CartItemService:

    @staticmethod
    async def add_item_into_cart(
        db: AsyncSession,
        user_id: int,
        item_data: CartItemAdd
    ):
        
        product = await product_crud.get_product_by_id(db, item_data.product_id)

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Товара с ID({item_data.product_id}) не найдено"
            )
        
        if product.is_delete:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Нельзя добавить в корзину удаленный товар"
            )
        
        if product.stock < item_data.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Недостаточно товара на складе. Доступно: {product.stock}"
            )
        
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