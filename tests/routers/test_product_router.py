import pytest
import io
from PIL import Image

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