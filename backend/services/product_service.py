from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from decimal import Decimal
from fastapi import UploadFile
from pathlib import Path
from PIL import Image
import io
import uuid
import aiofiles

from backend.crud.product import product_crud
from backend.crud.category import category_crud
from backend.schemas.product import ProductCreate, ProductEdit, ProductResponse
from backend.core.cache import cacheable, cache_invalidate

from backend.core.exceptions.product_exceptions import *
from backend.core.exceptions.category_exceptions import *

MAX_FILE_SIZE = 5 * 1024 * 1024
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}

class ProductService:
    
    @staticmethod
    @cache_invalidate(patterns=["products:*"])
    async def create_product(
        db: AsyncSession,
        product_data: ProductCreate
    ):
        category = await category_crud.get_category_by_id(db, product_data.category_id)

        if not category:
            raise CategoryNotFoundError(product_data.category_id)
        
        existing_product = await product_crud.get_product_by_name(db, product_data.name)

        if existing_product is not None:
            raise ProductAlreadyExistsError(product_data.name)
        
        product = await product_crud.create_product(db, product_data)

        await db.commit()
        await db.refresh(product)

        return product
    
    @staticmethod
    @cacheable(
        ttl=30,
        key="products:list:{skip}:{limit}:{min_price}:{max_price}:{category_id}:{show_deleted}",
        decoder=ProductResponse
    )
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
    @cacheable(ttl=60, key="products:by_id:{product_id}:{show_deleted}", decoder=ProductResponse)
    async def get_one_product_by_id(
        db: AsyncSession,
        product_id: int,
        show_deleted: bool = False
    ):
        
        product = await product_crud.get_product_by_id(db, product_id, show_deleted)

        if not product:
            raise ProductNotFoundError(product_id)
        
        return product
    
    @staticmethod
    @cacheable(ttl=20, key="products:search:{name_query}", decoder=ProductResponse)
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
    @cache_invalidate(patterns=["products:*"])
    async def edit_one_product_by_id(
        db: AsyncSession,
        product_id: int,
        updated_data: ProductEdit
    ):
        
        product = await product_crud.edit_product_by_id(db, product_id, updated_data)

        if product is None:
            raise ProductNotFoundError(product_id)
        
        await db.commit()
        await db.refresh(product)

        return product
    
    @staticmethod
    @cache_invalidate(patterns=["products:*"])
    async def delete_one_product_by_id(
        db: AsyncSession,
        product_id: int
    ):
        
        product = await product_crud.delete_product_by_id(db, product_id)

        if product is False or product is None:
            raise ProductNotFoundError(product_id)
        
        await db.commit()

        return {"message": f"Товар с ID({product_id}) успешно удален"}
    
    @staticmethod
    @cache_invalidate(patterns=["products:*"])
    async def restore_one_product_by_id(
        db: AsyncSession,
        product_id: int
    ):
        try:
            product = await product_crud.restore_product_by_id(db, product_id)

            if product is None:
                raise ProductNotFoundError(product_id)
            
            await db.commit()
            await db.refresh(product)

            return product
        
        except ValueError:
            raise ProductNotDeletedError()
    
    @staticmethod
    async def get_all_products_by_id(
        db: AsyncSession,
        category_id: int
    ):
        
        products = await product_crud.get_products_by_category(db, category_id)

        return products
    
    @staticmethod
    @cache_invalidate(patterns=["products:*"])
    async def update_product_image(
        db: AsyncSession,
        product_id: int,
        file: UploadFile
    ):
        
        product = await product_crud.get_product_by_id(db, product_id)

        if not product:
            raise ProductNotFoundError(product_id)

        if not file.filename:
            raise ProductMissingImageNameError()

        file_extension = file.filename.split(".")[-1].lower()

        if file_extension not in ALLOWED_EXTENSIONS:
            raise ProductInvalidImageExtensionError(ALLOWED_EXTENSIONS)

        content = await file.read()

        if len(content) > MAX_FILE_SIZE:
            raise ProductTooLargeImageError()

        try:
            image = Image.open(io.BytesIO(content))
            image.verify()

            if not image.format or image.format.lower() not in ["jpeg", "png"]:
                raise ProductInvalidImageFormatError()

        except ProductInvalidImageFormatError:
            raise
        except Exception:
            raise ProductInvalidImageError()

        base_dir = Path(__file__).resolve().parent.parent
        upload_dir = base_dir / "static" / "products"
        upload_dir.mkdir(parents=True, exist_ok=True)

        file_name = f"{uuid.uuid4()}.{file_extension}"
        full_save_path = upload_dir / file_name
        db_path = f"static/products/{file_name}"

        async with aiofiles.open(full_save_path, mode="wb") as buffer:
            await buffer.write(content)

        product.image_url = db_path
        await db.commit()
        await db.refresh(product)

        return product
    
product_service = ProductService()
