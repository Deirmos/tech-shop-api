from sqlalchemy.ext.asyncio import AsyncSession
from slugify import slugify

from backend.crud.category import category_crud
from backend.crud.product import product_crud
from backend.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from backend.core.cache import cacheable, cache_invalidate

from backend.core.exceptions.category_exceptions import *

class CategoryService:
    
    @staticmethod
    @cache_invalidate(patterns=["categories:*"])
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
    @cache_invalidate(patterns=["categories:*"])
    async def delete_one_category_by_id(
        db: AsyncSession,
        category_id: int
    ):
        
        products_in_category = await product_crud.get_products_by_category(db, category_id)

        if products_in_category:
            raise CategoryNotEmptyError()
        
        success = await category_crud.delete_category_by_id(db, category_id)

        if not success:
            raise CategoryNotFoundError(category_id)
        
        await db.commit()
        
        return True
    
    @staticmethod
    @cache_invalidate(patterns=["categories:*"])
    async def edit_one_category_by_id(
        db: AsyncSession,
        category_id: int,
        updated_data: CategoryUpdate
    ):
        
        category = await category_crud.edit_category_by_id(db, category_id, updated_data)

        if category is None:
            raise CategoryNotFoundError(category_id)
        
        await db.commit()
        await db.refresh(category)

        return category
    
    @staticmethod
    @cacheable(ttl=120, key="categories:by_id:{category_id}", decoder=CategoryResponse)
    async def get_one_category_by_id(
        db: AsyncSession,
        category_id: int
    ):
        
        category = await category_crud.get_category_by_id(db, category_id)

        if category is None or category.is_delete == True:
            raise CategoryNotFoundError(category_id)
        
        return category
    
    @staticmethod
    @cacheable(ttl=60, key="categories:list:{skip}:{limit}", decoder=CategoryResponse)
    async def get_all_categories(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 10
    ):
        
        categories = await category_crud.get_all_categories(
            db,
            skip=skip,
            limit=limit
        )

        return categories
    
    @staticmethod
    async def get_all_categories_for_admin(
        db: AsyncSession,
        is_delete: bool,
        skip: int = 0,
        limit: int = 10
    ):
        
        categories = await category_crud.get_all_categories_for_admin(
            db,
            is_delete=is_delete,
            skip=skip,
            limit=limit
        )

        return categories
    
    @staticmethod
    @cache_invalidate(patterns=["categories:*"])
    async def restore_category(
        db: AsyncSession,
        category_id: int
    ):
        try:
            category = await category_crud.restore_category_by_id(db, category_id)

            if category is None:
                raise CategoryNotFoundError(category_id)
            
            await db.commit()
            await db.refresh(category)

            return category
        
        except ValueError:
            raise CategoryNotDeletedError()
        
            
category_service = CategoryService()
