import pytest
from fastapi import HTTPException, status

from backend.services.product_service import product_service
from backend.schemas.product import ProductCreate, ProductEdit
from backend.models.product import Product

@pytest.mark.asyncio
class TestProductService:

    async def test_create_product_success(self, db_session, category_factory):
        cat = await category_factory()

        data = ProductCreate(
            name="New iPhone",
            description="Classic",
            price=999.99,
            stock=10,
            category_id=cat.id
        )

        product = await product_service.create_product(db_session, data)

        assert product.name == "New iPhone"
        assert product.category_id == cat.id

    async def test_create_product_category_not_found(self, db_session):
        data = ProductCreate(name="Test Product", description="Test Desc", price=10, stock=1, category_id=-1)

        with pytest.raises(HTTPException) as excinfo:
            await product_service.create_product(db_session, data)

        assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND
        assert "Категории с id -1 не найдено" in excinfo.value.detail

    async def test_create_product_duplicate_name(self, db_session, category_factory, product_factory):
        cat = await category_factory()
        
        await product_factory(name="Duplicate", category_id=cat.id)

        data = ProductCreate(name="Duplicate", description="Test Desc", price=10, stock=10, category_id=cat.id)

        with pytest.raises(HTTPException) as excinfo:
            await product_service.create_product(db_session, data)

        assert excinfo.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "уже существует" in excinfo.value.detail

    async def test_get_one_product_success(self, db_session, category_factory, product_factory):
        cat = await category_factory()
        
        product = await product_factory(name="Test Product", category_id=cat.id)

        product_found = await product_service.get_one_product_by_id(db_session, product.id)

        assert product_found.id == product.id
        assert product_found.name == product.name

    async def test_get_one_product_not_found(self, db_session):
        with pytest.raises(HTTPException) as excinfo:
            await product_service.get_one_product_by_id(db_session, -1)

        assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND
        assert excinfo.value.detail == "Товара с ID(-1) не найдено"

    async def test_search_product_logic(self, db_session, product_factory):
        await product_factory(name="Super Computer")

        results = await product_service.search_products_by_name(db_session, "  Super  ")
        assert len(results) >= 1
        assert "Super Computer" in results[0].name

        short_results = await product_service.search_products_by_name(db_session, "a")
        assert short_results == []

    async def test_edit_product_success(self, db_session, product_factory):
        product = await product_factory(name="Old Name")
        update_data = ProductEdit(name="New Name")

        updated = await product_service.edit_one_product_by_id(db_session, product.id, update_data)
        assert updated.name == "New Name"

    async def test_delete_and_restore_cycle(self, db_session, product_factory):
        product = await product_factory(name="To Be Deleted")

        delete_res = await product_service.delete_one_product_by_id(db_session, product.id)
        assert "успешно удален" in delete_res["message"]

        await db_session.refresh(product)
        assert product.is_delete is True

        restored = await product_service.restore_one_product_by_id(db_session, product.id)
        assert restored.is_delete is False

    async def test_delete_product_not_found(self, db_session):
        with pytest.raises(HTTPException) as excinfo:
            await product_service.delete_one_product_by_id(db_session, -1)

        assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND
        assert excinfo.value.detail == "Товара с ID(-1) не найдено"

    async def test_restore_error_logic(self, db_session, product_factory):
        product = await product_factory(name="Not Deleted Yet")

        with pytest.raises(HTTPException) as excinfo:
            await product_service.restore_one_product_by_id(db_session, product.id)
        
        assert excinfo.value.status_code == status.HTTP_400_BAD_REQUEST

    async def test_restore_product_not_found(self, db_session):
        with pytest.raises(HTTPException) as excinfo:
            await product_service.restore_one_product_by_id(db_session, -1)

        assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND
        assert excinfo.value.detail == "Товара с ID(-1) не найдено"

    async def test_get_products_list(
            self,
            db_session,
            product_factory,
            category_factory
    ):
        category1 = await category_factory(name="Cat 1")
        category2 = await category_factory(name="Cat 2")
        category3 = await category_factory(name="Cat 3")
        category4 = await category_factory(name="Cat 4")

        await product_factory(name="Product 1", price=100, category_id=category1.id)
        await product_factory(name="Product 2", price=2000, category_id=category2.id)
        await product_factory(name="Product 3", price=10000, category_id=category3.id)
        await product_factory(name="Product 4", price=10, category_id=category4.id)

        list1 = await product_service.get_products_list(db_session, min_price=1000, max_price=2000)
        assert {p.name for p in list1} == {"Product 2"}
        
        list2 = await product_service.get_products_list(db_session, category_id=category3.id)
        assert {p.name for p in list2} == {"Product 3"}

        list3 = await product_service.get_products_list(db_session, skip=1, limit=2)
        assert len(list3) == 2
        assert {p.name for p in list3} == {"Product 2", "Product 3"}

    async def test_get_all_products_by_id(
            self,
            db_session,
            category_factory,
            product_factory
    ):
        
        category1 = await category_factory(name="Cat 1")
        category2 = await category_factory(name="Cat 2")

        await product_factory(name="Product 1", category_id=category1.id)
        await product_factory(name="Product 2", category_id=category1.id)
        await product_factory(name="Product 3", category_id=category2.id)
        await product_factory(name="Product 4", category_id=category2.id)

        list1 = await product_service.get_all_products_by_id(db_session, category1.id)
        assert len(list1) == 2
        assert {p.name for p in list1} == {"Product 1", "Product 2"}

        list2 = await product_service.get_all_products_by_id(db_session, category2.id)
        assert len(list2) == 2
        assert {p.name for p in list2} == {"Product 3", "Product 4"}
