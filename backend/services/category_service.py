from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from slugify import slugify

from backend.crud.category import category_crud
from backend.crud.product import product_crud
from backend.schemas.category import CategoryCreate, CategoryUpdate

class CategoryService:
    
    @staticmethod
    async def create_category(
        db: AsyncSession,
        category_data: CategoryCreate
    ):
        category_dict = category_data.model_dump()

        if not category_dict.get("slug"):
            category_dict["slug"] = slugify(category_dict["name"])
        else:
            category_dict["slug"] = slugify(category_dict["slug"])

        category = await category_crud.create_new_category(db, category_dict)

        await db.commit()
        await db.refresh(category)

        return category
    
    @staticmethod
    async def delete_one_category_by_id(
        db: AsyncSession,
        category_id: int
    ):
        
        products_in_category = await product_crud.get_products_by_category(db, category_id)

        if products_in_category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Нельзя удалить категорию, пока в ней есть товары"
            )
        
        success = await category_crud.delete_category_by_id(db, category_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Категории не найдено"
            )
        
        await db.commit()
        return True
    
    @staticmethod
    async def edit_one_category_by_id(
        db: AsyncSession,
        category_id: int,
        updated_data: CategoryUpdate
    ):
        
        category = await category_crud.edit_category_by_id(db, category_id, updated_data)

        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Категории под ID({category_id}) не найдено"
            )
        
        await db.commit()
        await db.refresh(category)

        return category
    
    @staticmethod
    async def get_one_category_by_id(
        db: AsyncSession,
        category_id: int
    ):
        
        category = await category_crud.get_category_by_id(db, category_id)

        if category is None or category.is_delete == True:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Категории с ID({category_id}) не найдено"
            )
        
        return category
    
    @staticmethod
    async def get_all_categories(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 10
    ):
        
        categories = await category_crud._get_all_categories(
            db,
            skip=skip,
            limit=limit
        )

        return categories
    
category_service = CategoryService()