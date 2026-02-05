import pytest
from fastapi import HTTPException, status

from backend.models.category import Category
from backend.services.category_service import category_service
from backend.schemas.category import CategoryCreate, CategoryUpdate

@pytest.mark.asyncio
class TestCategoryService:

    async def test_create_category(
            self,
            db_session
    ):

        category_data = CategoryCreate(
            name="Test Category"
        )

        category = await category_service.create_category(db_session, category_data)

        assert category is not None
        assert category.name == "Test Category"

    async def test_delete_one_category_by_id_success(
            self,
            db_session,
            category_factory
    ):
        
        category = await category_factory(name="Delete Test")

        await category_service.delete_one_category_by_id(db_session, category.id)

        assert category.is_delete == True

    async def test_delete_one_category_by_id_not_found(
            self,
            db_session,
    ):
        
        with pytest.raises(HTTPException) as excinfo:
            await category_service.delete_one_category_by_id(db_session, -1)

        assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND
        assert "Категории не найдено" in excinfo.value.detail

    async def test_delete_one_category_by_id_product_error(
            self,
            db_session,
            product_factory,
            category_factory
    ):
        
        category = await category_factory(name="Product Error")

        await product_factory(name="Test Product", category_id=category.id)

        with pytest.raises(HTTPException) as excinfo:
            await category_service.delete_one_category_by_id(db_session, category.id)
        
        assert excinfo.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Нельзя удалить категорию" in excinfo.value.detail

    async def test_edit_one_category_by_id_success(
            self,
            db_session,
            category_factory
    ):
        
        category = await category_factory(name="To edit")

        updated_data = CategoryUpdate(
            name="Updated category"
        )

        updated_category = await category_service.edit_one_category_by_id(
            db_session,
            category.id,
            updated_data
        )

        assert updated_category.name == "Updated category"
        assert updated_category.id == category.id

    async def test_edit_one_category_by_id_not_found(
            self,
            db_session
    ):
        
        updated_data = CategoryUpdate(name="Not found")

        with pytest.raises(HTTPException) as excinfo:
            await category_service.edit_one_category_by_id(
                db_session,
                -1,
                updated_data
            )
        
        assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND
        assert "Категории под ID(-1) не найдено" in excinfo.value.detail

    async def test_get_one_category_by_id_success(
            self,
            db_session,
            category_factory
    ):
        
        category = await category_factory(name="Success")

        category_found = await category_service.get_one_category_by_id(
            db_session,
            category.id
        )

        assert category_found.id == category.id
        assert category_found.name == category.name

    async def test_get_one_category_by_id_not_found(
            self,
            db_session
    ):
        
        with pytest.raises(HTTPException) as excinfo:
            await category_service.get_one_category_by_id(
                db_session,
                -1
            )

        assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND
        assert "Категории с ID(-1) не найдено" in excinfo.value.detail

    async def test_get_all_categories_with_pagination(
            self,
            db_session,
            category_factory
    ):
        
        await category_factory(name="Cat 1")
        cat2 = await category_factory(name="Cat 2")
        cat3 = await category_factory(name="Cat 3")
        await category_factory(name="Cat 4")

        categories = await category_service.get_all_categories(db_session, skip=1, limit=2)

        assert len(categories) == 2
        assert cat2 in categories and cat3 in categories