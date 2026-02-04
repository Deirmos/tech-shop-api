from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from backend.models.category import Category
from backend.schemas.category import CategoryCreate, CategoryUpdate

class CategoryCRUD:

    @staticmethod
    async def _get_all_categories(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 10
    ) -> List[Category]:
        query = select(Category).offset(skip).limit(limit)

        categories = await db.execute(query)

        return categories.scalars().all()

    @staticmethod
    async def get_category_by_id(
        db: AsyncSession,
        category_id: int
    ) -> Category | None:
        
        category = await db.execute(select(Category).where(Category.id == category_id))

        return category.scalar_one_or_none()
    
    @staticmethod
    async def create_new_category(
        db: AsyncSession,
        category_data: CategoryCreate
    ) -> Category:
        
        category = Category(
            **category_data
        )

        db.add(category)
        await db.flush()

        return category
    
    @staticmethod
    async def edit_category_by_id(
        db: AsyncSession,
        category_id: int,
        updated_data: CategoryUpdate
    ) -> Category | None:
        
        category = await CategoryCRUD.get_category_by_id(db, category_id)

        if not category:
            return None
        
        update_dict = updated_data.model_dump(exclude_unset=True)

        for field, value in update_dict.items():
            setattr(category, field, value)

        await db.flush()
        await db.refresh(category)

        return category
    
    @staticmethod
    async def delete_category_by_id(
        db: AsyncSession,
        category_id: int
    ) -> bool:
        
        category = await CategoryCRUD.get_category_by_id(db, category_id)

        if not category:
            return False
        
        category.is_delete = True

        await db.flush()

        return True
    
category_crud = CategoryCRUD()