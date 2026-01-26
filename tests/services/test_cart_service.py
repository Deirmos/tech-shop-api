import pytest
from fastapi import HTTPException, status

from backend.services.cart_service import cart_service
from backend.models.cart import CartItem
from backend.schemas.cart import CartItemAdd, CartSummary

@pytest.mark.asyncio
class TestCartService:

    async def test_add_item_into_cart_success(
            self,
            db_session,
            product_factory,
            user_factory
    ):
        
        user = await user_factory(email="testuser@example.com")
        product = await product_factory(name="Cart test", price=100, stock=10)
        quantity_to_add = 2

        item_data = CartItemAdd(
            product_id=product.id,
            quantity=quantity_to_add
        )

        cart_item = await cart_service.add_item_into_cart(db_session, user.id, item_data)

        assert cart_item.user_id == user.id
        assert cart_item.product_id == product.id
        assert cart_item.quantity == quantity_to_add

        assert cart_item.product is not None
        assert cart_item.product.name == "Cart test"
        assert cart_item.product.price == 100

    async def test_add_item_into_cart_errors(
            self,
            db_session,
            product_factory,
            user_factory
    ):
        
        user = await user_factory(email="testuser@example.com")
        quantity_to_add = 2

        item_data = CartItemAdd(
            product_id=-1,
            quantity=quantity_to_add
        )

        with pytest.raises(HTTPException) as excinfo:
            await cart_service.add_item_into_cart(db_session, user.id, item_data)

        assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND
        assert "Товара с ID(-1) не найдено" in excinfo.value.detail

        product = await product_factory(name="Cart test", price=100, stock=10, is_delete=True)

        item_data2 = CartItemAdd(
            product_id=product.id,
            quantity=quantity_to_add
        )

        with pytest.raises(HTTPException) as exc1:
            await cart_service.add_item_into_cart(db_session, user.id, item_data2)

        assert exc1.value.status_code == status.HTTP_404_NOT_FOUND
        assert "не найдено" in exc1.value.detail

        product2 = await product_factory(name="Cart test 2", price=100, stock=1)

        item_data3 = CartItemAdd(
            product_id=product2.id,
            quantity=5
        )

        with pytest.raises(HTTPException) as exc2:
            await cart_service.add_item_into_cart(db_session, user.id, item_data3)

        assert exc2.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Недостаточно товара на складе" in exc2.value.detail

    async def test_get_my_cart(
            self,
            db_session,
            user_factory,
            cart_item_factory,
            product_factory
    ):
        
        user = await user_factory(email="testuser@example.com")
        p1 = await product_factory(name="Product 1", price=100, stock=10)
        p2 = await product_factory(name="Product 2", price=250, stock=5)

        await cart_service.add_item_into_cart(db_session, user.id,
                CartItemAdd(product_id=p1.id, quantity=2))
        await cart_service.add_item_into_cart(db_session, user.id,
                CartItemAdd(product_id=p2.id, quantity=1))
        
        #Итого: 450

        user_cart = await cart_service.get_my_cart(db_session, user.id)

        assert "items" in user_cart
        assert "total_price" in user_cart

        assert len(user_cart["items"]) == 2

        expected_total = (100 * 2) + (250 * 1)
        assert user_cart["total_price"] == expected_total

        assert user_cart["items"][0].product.name is not None

    async def test_clear_cart(
            self,
            db_session,
            user_factory,
            cart_item_factory,
            product_factory
    ):
        
        user = await user_factory(email="testuser@example.com")

        p1 = await product_factory(name="Product 1", price=100, stock=5)
        p2 = await product_factory(name="Product 2", price=200, stock=5)

        await cart_service.add_item_into_cart(db_session, user.id, 
                CartItemAdd(product_id=p1.id, quantity=1))
        await cart_service.add_item_into_cart(db_session, user.id,
                CartItemAdd(product_id=p2.id, quantity=1))

        await cart_service.clear_cart(db_session, user.id)

        cleared_cart = await cart_service.get_my_cart(db_session, user.id)

        assert cleared_cart["items"] == []
        assert cleared_cart["total_price"] == 0