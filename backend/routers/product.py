from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from fastapi import UploadFile, File
import shutil
import uuid
from pathlib import Path

from backend.schemas.product import ProductResponse, ProductCreate, ProductEdit
from backend.models.user import User
from backend.services.user_service import user_service, get_current_admin_user
from backend.services.product_service import product_service
from backend.core.database import get_db

router = APIRouter(prefix="/product", tags=["products"])

admin_router = APIRouter(prefix="/admin/product", tags=["admin-products"])

@router.get("/", response_model=List[ProductResponse])
async def get_all_products(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 10,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    category_id: Optional[int] = None
):
    
    products = await product_service.get_products_list(
        db,
        skip=skip,
        limit=limit,
        min_price=min_price,
        max_price=max_price,
        category_id=category_id
    )

    return products

@router.get("/{product_id}", response_model=ProductResponse)
async def get_product_by_id(
    product_id: int,
    db: AsyncSession = Depends(get_db)
):
    
    product = await product_service.get_one_product_by_id(db, product_id)

    return product

@admin_router.get("/", response_model=List[ProductResponse])
async def get_all_products_for_admin(
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    
    return await product_service.get_products_list(
        db,
        skip=skip,
        limit=limit,
        show_deleted=True
    )

@admin_router.get("/{product_id}", response_model=ProductResponse)
async def get_product_by_id_for_admin(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    
    product = await product_service.get_one_product_by_id(db, product_id, show_deleted=True)

    return product

@admin_router.patch("/{product_id}/restore", response_model=ProductResponse)
async def restore_product_by_id(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    
    product = await product_service.restore_one_product_by_id(db, product_id)

    return product

@admin_router.patch("/{product_id}/image", response_model=ProductResponse)
async def upload_product_image(
    product_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin_user)
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Можно загружать только изображения"
        )

    BASE_DIR = Path(__file__).resolve().parent.parent
    upload_dir = BASE_DIR / "static" / "products"
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    file_name = f"{uuid.uuid4()}.{file.filename.split('.')[-1]}"
    full_save_path = upload_dir / file_name
    db_path = f"static/products/{file_name}"

    content = await file.read() 
    with open(full_save_path, "wb") as buffer:
        buffer.write(content)

    product = await product_service.update_product_image(db, product_id, db_path)
    return product

@router.get("/name/{product_name}", response_model=List[ProductResponse])
async def search_products(
    product_name: str,
    db: AsyncSession = Depends(get_db)
):
    
    products = await product_service.search_products_by_name(db, product_name)

    return products

@router.put("/{product_id}", response_model=ProductResponse)
async def edit_product_by_id(
    product_id: int,
    updated_data: ProductEdit,
    user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    
    product = await product_service.edit_one_product_by_id(db, product_id, updated_data)

    return product

@admin_router.post("/", response_model=ProductResponse)
async def create_product(
    product_data: ProductCreate,
    user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    
    product = await product_service.create_product(db, product_data)

    return product

@router.delete("/{product_id}")
async def delete_product(
    product_id: int,
    user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    
    return await product_service.delete_one_product_by_id(db, product_id)
