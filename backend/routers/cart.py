from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_db
from backend.services.user_service import get_current_user
from backend.models.user import User
from backend.schemas.cart import CartItemAdd, CartItemResponse
from backend.services.cart_service import cart_service

router = APIRouter(prefix="/cart", tags=["Cart"])

@router.post("/", response_model=CartItemResponse)
async def add_to_cart(
    item_data: CartItemAdd,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    
    return await cart_service.add_item_into_cart(db, current_user.id, item_data)

@router.get("/")
async def get_my_cart(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    
    return await cart_service.get_my_cart(db, current_user.id)

@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def clear_my_cart(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    
    await cart_service.clear_cart(db, current_user.id)
    
    return None