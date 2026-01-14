from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import joinedload
from typing import List

from backend.models.cart import CartItem

class CartItemCRUD:

    @staticmethod
    async def get_cart_item(
        db: AsyncSession,
        product_id: int,
        user_id: int
    ):
        
        result = await db.execute(
            select(CartItem).where(
                CartItem.user_id == user_id,
                CartItem.product_id == product_id
            )
        )

        return result.scalars().first()
    

    @staticmethod
    async def add_product_into_cart(
        db: AsyncSession,
        user_id: int,
        product_id: int,
        quantity: int = 1
    ):
        
        item = await CartItemCRUD.get_cart_item(db, product_id, user_id)

        if item:
            item.quantity += quantity
        else:
            item = CartItem(
                user_id=user_id,
                product_id=product_id,
                quantity=quantity
            )

        db.add(item)
        await db.flush()

        return item
        
    @staticmethod
    async def get_user_cart(
        db: AsyncSession,
        user_id: int
    ):

      result = await db.execute(
          select(CartItem)
          .where(CartItem.user_id == user_id)
          .options(joinedload(CartItem.product))
      )

      return result.scalars().all()
    
    @staticmethod
    async def delete_all_cart_items_by_user_id(
        db: AsyncSession,
        user_id: int
    ):
        
        stmt = delete(CartItem).where(CartItem.user_id == user_id)

        await db.execute(stmt)

        await db.flush()

cart_crud = CartItemCRUD()
