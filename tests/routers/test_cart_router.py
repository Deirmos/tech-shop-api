import pytest

@pytest.mark.asyncio
class TestCartRouter:

    async def test_get_my_cart(
            self,
            auth_client,
            cart_item_factory,
            product_factory,
            user
    ):
        product1 = await product_factory(
            name="Product 1", price=100, stock=5
        )

        product2 = await product_factory(
            name="Product 2", price=200, stock=3
        )

        await cart_item_factory(
            user_id=user.id,
            product_id=product1.id,
            quantity=3
        )

        await cart_item_factory(
            user_id=user.id,
            product_id=product2.id,
            quantity=2
        )

        response = await auth_client.get("/api/cart/")

        assert response.status_code == 200

        data = response.json()

        items = data["items"]
        assert len(items) == 2

        item_map = {item["product_id"]: item for item in items}

        assert product1.id in item_map
        assert item_map[product1.id]["quantity"] == 3
        
        assert product2.id in item_map
        assert item_map[product2.id]["quantity"] == 2

    async def test_clear_my_cart(
            self,
            auth_client,
            user,
            product_factory,
            cart_item_factory
    ):
        product1 = await product_factory(name="Product 1")
        product2 = await product_factory(name="Product 2")

        await cart_item_factory(
            user_id=user.id,
            product_id=product1.id,
            quantity=1
        )

        await cart_item_factory(
            user_id=user.id,
            product_id=product2.id,
            quantity=1
        )

        response = await auth_client.delete("/api/cart/")
        
        response.status_code == 204

        