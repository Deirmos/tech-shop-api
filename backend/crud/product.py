from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from decimal import Decimal
from typing import Optional

from backend.models.product import Product
from backend.schemas.product import ProductCreate, ProductEdit

class ProductCRUD:

    @staticmethod
    async def get_all_products(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 10,
        min_price: Optional[Decimal] = None,
        max_price: Optional[Decimal] = None,
        category_id: Optional[int] = None,
        show_deleted: bool = False
    ):
        
        query = select(Product)

        if not show_deleted:
            query = query.where(Product.is_delete == False)

        if min_price:
            query = query.where(Product.price >= min_price)

        if max_price:
            query = query.where(Product.price <= max_price)

        if category_id:
            query = query.where(Product.category_id == category_id)

        query = query.order_by(Product.id.asc()).offset(skip).limit(limit)

        products = await db.execute(query)

        return products.scalars().all()

    @staticmethod
    async def get_product_by_id(
        db: AsyncSession,
        product_id: int,
        show_deleted: bool = False
    ) -> Product | None:
        
        query = select(Product).where(Product.id == product_id)

        if not show_deleted:
            query = query.where(Product.is_delete == False)

        result = await db.execute(query)

        return result.scalar_one_or_none()
    
    @staticmethod
    async def seacrh_products_by_name(
        db: AsyncSession,
        name_query: str,
        limit: int = 10
    ) -> list[Product]:
        
        word_sim = func.word_similarity(Product.name, name_query)

        full_sim = func.similarity(Product.name, name_query)

        query = (
            select(Product)
            .where(
                or_(
                    Product.name.ilike(f"%{name_query}%"),
                    word_sim > 0.4,
                    full_sim > 0.1,
                ),
                Product.is_delete == False
            )
            .order_by(word_sim.desc(), full_sim.desc())
            .limit(limit)
        )

        result = await db.execute(query)

        return result.scalars().all()
    
    @staticmethod
    async def create_product(
        db: AsyncSession,
        product_data: ProductCreate
    ) -> Product:
        product = Product(
            **product_data.model_dump()
        )

        db.add(product)
        await db.flush()
        await db.refresh(product)

        return product
    
    @staticmethod
    async def edit_product_by_id(
        db: AsyncSession,
        product_id: int,
        updated_data: ProductEdit
    ) -> Product | None:
        
        product = await ProductCRUD.get_product_by_id(db, product_id)

        if not product:
            return None
        
        update_dict = updated_data.model_dump(exclude_unset=True)

        for field, value in update_dict.items():
            setattr(product, field, value)

        await db.flush()

        return product
    
    @staticmethod
    async def delete_product_by_id(
        db: AsyncSession,
        product_id: int
    ) -> bool:
        
        product = await ProductCRUD.get_product_by_id(db, product_id)

        if not product:
            return False
        
        product.is_delete = True

        await db.flush()

        return True
    
    @staticmethod
    async def restore_product_by_id(
        db: AsyncSession,
        product_id: int
    ):

        product = await ProductCRUD.get_product_by_id(db, product_id, show_deleted=True)

        if not product:
            return None
        
        if not product.is_delete:
            raise ValueError("Нельзя восстановить не удаленный товар")
        
        product.is_delete = False

        await db.flush()

        return product
    
    @staticmethod
    async def get_products_by_category(
        db: AsyncSession,
        category_id: int
    ):
        
        result = await db.execute(select(Product).where(Product.category_id == category_id, Product.is_delete == False))

        return result.scalars().all()
    
    @staticmethod
    async def get_product_by_name(
        db: AsyncSession,
        product_name: str
    ):
        
        product = await db.execute(select(Product).where(Product.name == product_name))

        if not product:
            return None

        return product.scalar_one_or_none()

product_crud = ProductCRUD()