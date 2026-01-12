from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from backend.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate
from backend.models.user import User
from backend.services.category_service import category_service
from backend.services.user_service import user_service, get_current_admin_user
from backend.core.database import get_db

router = APIRouter(prefix="/category", tags=["categories"])

@router.post("/", response_model=CategoryResponse)
async def create_new_category(
    category_data: CategoryCreate,
    user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    
    category = await category_service.create_category(db, category_data)

    return category

@router.get("/", response_model=List[CategoryResponse])
async def get_categories(
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    
    categories = await category_service.get_all_categories(
        db,
        skip=skip,
        limit=limit
    )

    return categories

@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: int,
    db: AsyncSession = Depends(get_db)
):
    
    category = await category_service.get_one_category_by_id(db, category_id)

    return category

@router.put("/{category_id}", response_model=CategoryResponse)
async def edit_category(
    category_id: int,
    updated_data: CategoryUpdate,
    user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    
    category = await category_service.edit_one_category_by_id(db, category_id, updated_data)

    return category

@router.delete("/{category_id}")
async def delete_category(
    category_id: int,
    user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    
    return await category_service.delete_one_category_by_id(db, category_id)