import pytest
import io
from PIL import Image

from backend.schemas.product import ProductCreate

@pytest.mark.asyncio
class TestProductRouter:

    async def test_get_all_products_success(
            self,
            async_client,
            product_factory
    ):
        
        await product_factory(name="Phone", price=500)
        await product_factory(name="Laptop", price=1500)

        response = await async_client.get("/api/product/")
        assert response.status_code == 200
        assert len(response.json()) >= 2

    async def test_search_products_by_name(
            self,
            async_client,
            product_factory
    ):
        
        await product_factory(name="Super Gadget")

        response = await async_client.get("/api/product/name/Super")
        assert response.status_code == 200
        assert any(item["name"] == "Super Gadget" for item in response.json())

    async def test_create_product_forbidden_for_user(
            self,
            auth_client
    ):
        
        payload = {
            "name": "Admin Product",
            "description": "Should fail",
            "price": 100,
            "stock": 10,
            "category_id": 1
        }

        response = await auth_client.post("/api/admin/product", json=payload)

        assert response.status_code == 307

    async def test_upload_product_image_success(
            self,
            admin_client,
            product_factory,
    ):
        
      
        product = await product_factory()

        file_content = b"fake image content"

        file_data = io.BytesIO()
        image = Image.new('RGB', size=(10, 10), color=(255, 0, 0))
        image.save(file_data, format="JPEG")
        file_data.seek(0)


        response = await admin_client.patch(
            f"/api/admin/product/{product.id}/image",
            files={"file": ("test.jpg", file_data, "image/jpeg")},
        )

        assert response.status_code == 200
        data = response.json()
        assert "image_url" in data

    async def test_edit_product_by_id(
            self,
            admin_client,
            product_factory
    ):
        product_to_edit = await product_factory(
            name="Product test",
            description="Test desc",
            price=1000,
            stock=10
        )

        response = await admin_client.put(
            f"/api/admin/product/{product_to_edit.id}",
            json={"name": "Edited product",
                  "description": "Good desc",
                  "price": 500,
                  "stock": 5}
            )

        assert response.status_code == 200

        data = response.json()

        assert data["id"] == product_to_edit.id
        assert data["name"] == "Edited product"
        assert data["price"] == "500.00"

    async def test_create_product_success(
            self,
            admin_client,
            category_factory,
            user
    ):
        category1 = await category_factory(name="Category 1")
        
        product_data = ProductCreate(
            name="Test product",
            description="Test desc",
            price=500,
            stock=10,
            category_id=category1.id
        )

        response = await admin_client.post(
            "/api/admin/product/",
            json=product_data.model_dump(mode="json")
        )

        assert response.status_code == 200

        data = response.json()

        assert data["name"] == "Test product"
        assert data["price"] == "500.00"

    async def test_delete_product_success(
            self,
            product_factory,
            admin_client
    ):
        product = await product_factory(name="Product 1")

        response = await admin_client.delete(f"/api/admin/product/{product.id}")

        assert response.status_code == 200

    async def test_delete_product_not_found(
            self,
            admin_client
    ):
        response = await admin_client.delete(f"/api/admin/product/{-1}")

        assert response.status_code == 404