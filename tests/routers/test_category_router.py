import pytest

from backend.schemas.category import CategoryCreate, CategoryUpdate

@pytest.mark.asyncio
class TestCategoryRouter:

    async def test_create_new_category(
            self,
            admin_client,
    ):
        
        category_data = CategoryCreate(
            name="Test Category",
            slug="",
            description="Category for tests"
        )
        
        response = await admin_client.post(
            "/api/admin/category/",
            json=category_data.model_dump()
        )
        
        assert response.status_code == 200

        data = response.json()

        assert data["name"] == "Test Category"

    async def test_get_categories(
            self,
            auth_client,
            category_factory
    ):
        category1 = await category_factory(name="Category 1")
        category2 = await category_factory(name="Category 2")

        response = await auth_client.get("/api/category/")

        assert response.status_code == 200

        data = response.json()

        assert data[0]["id"] == category1.id
        assert data[1]["id"] == category2.id

    async def test_get_categories_with_pagination(
            self,
            auth_client,
            category_factory
    ):
        category1 = await category_factory(name="Category 1")
        category2 = await category_factory(name="Category 2")
        category3 = await category_factory(name="Category 3")

        response = await auth_client.get(
            "/api/category/",
            params={"skip": 1, "limit": 1}
        )

        assert response.status_code == 200

        data = response.json()

        assert len(data) == 1
        assert data[0]["id"] == category2.id

    async def test_get_category_found(
            self,
            auth_client,
            category_factory
    ):
        category = await category_factory()

        response = await auth_client.get(f"/api/category/{category.id}")

        assert response.status_code == 200

        data = response.json()

        assert data["id"] == category.id

    async def test_get_category_not_found(
            self,
            auth_client
    ):
        
        response = await auth_client.get(f"/api/category/{-1}")

        assert response.status_code == 404

    async def test_edit_category_success(
            self,
            admin_client,
            category_factory
    ):
        category = await category_factory()

        response = await admin_client.put(
            f"/api/admin/category/{category.id}",
            json={
                "name": "Edited category",
                "slug": "",
                "description": "This category has been edited"
            }
        )

        assert response.status_code == 200

        data = response.json()

        assert data["id"] == category.id
        assert data["name"] == "Edited category"

    async def test_delete_category_success(
            self,
            admin_client,
            category_factory
    ):
        category = await category_factory()

        response = await admin_client.delete(f"/api/admin/category/{category.id}")

        assert response.status_code == 200
        assert category.is_delete == True

    async def test_delete_category_error(
            self,
            admin_client,
            category_factory,
            product_factory
    ):
        category = await category_factory(name="Error")

        await product_factory(name="Invincible", category_id=category.id)

        response = await admin_client.delete(f"/api/admin/category/{category.id}")

        assert response.status_code == 400

