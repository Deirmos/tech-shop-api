from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from typing import Optional
from decimal import Decimal

from backend.crud.product import product_crud
from backend.crud.category import category_crud
from backend.schemas.product import ProductCreate, ProductEdit

class ProductService:
    
    @staticmethod
    async def create_product(
        db: AsyncSession,
        product_data: ProductCreate
    ):
        category = await category_crud.get_category_by_id(db, product_data.category_id)

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Категории с id {product_data.category_id} не найдено"
            )
        
        existing_product = await product_crud.get_product_by_name(db, product_data.name)

        if existing_product is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Товар с таким именем уже существует"
            )
        
        product = await product_crud.create_product(db, product_data)

        await db.commit()
        await db.refresh(product)

        return product
    
    @staticmethod
    async def get_products_list(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 10,
        min_price: Optional[Decimal] = None,
        max_price: Optional[Decimal] = None,
        category_id: Optional[int] = None,
        show_deleted: bool = False
    ):

        return await product_crud.get_all_products(
            db,
            skip=skip,
            limit=limit,
            min_price=min_price,
            max_price=max_price,
            category_id=category_id,
            show_deleted=show_deleted
        )
    
    @staticmethod
    async def get_one_product_by_id(
        db: AsyncSession,
        product_id: int,
        show_deleted: bool = False
    ):
        
        product = await product_crud.get_product_by_id(db, product_id, show_deleted)

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Товара с ID({product_id}) не найдено"
            )
        
        return product
    
    @staticmethod
    async def search_products_by_name(
        db: AsyncSession,
        name_query: str
    ):
        
        clean_query = name_query.strip()

        if len(clean_query) < 2:
            return []
        
        products = await product_crud.seacrh_products_by_name(db, clean_query)

        return products
    
    @staticmethod
    async def edit_one_product_by_id(
        db: AsyncSession,
        product_id: int,
        updated_data: ProductEdit
    ):
        
        product = await product_crud.edit_product_by_id(db, product_id, updated_data)

        if product is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Товара с ID({product_id}) не найдено"
            )
        
        await db.commit()
        await db.refresh(product)

        return product
    
    @staticmethod
    async def delete_one_product_by_id(
        db: AsyncSession,
        product_id: int
    ):
        
        product = await product_crud.delete_product_by_id(db, product_id)

        if product is False:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Товара с ID({product_id}) не найдено"
            )
        
        await db.commit()

        return {"message": f"Товар с ID({product_id}) успешно удален"}
    
    @staticmethod
    async def restore_one_product_by_id(
        db: AsyncSession,
        product_id: int
    ):
        try:
            product = await product_crud.restore_product_by_id(db, product_id)

            if product is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Товара с ID({product_id}) не найдено"
                )
            
            await db.commit()
            await db.refresh(product)

            return product
        
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
    
    @staticmethod
    async def get_all_products_by_id(
        db: AsyncSession,
        category_id: int
    ):
        
        products = await product_crud.get_products_by_category(db, category_id)

        return products
    
    @staticmethod
    async def update_product_image(
        db: AsyncSession,
        product_id: int,
        image_path: str
    ):
        
        product = await product_crud.get_product_by_id(db, product_id)

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Товара под ID({product_id}) не найдено"
            )
        
        product.image_url = image_path
        await db.commit()
        await db.refresh(product)

        return product
    
product_service = ProductService()