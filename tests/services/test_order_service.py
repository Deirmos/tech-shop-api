import pytest
from fastapi import HTTPException, status
from fastapi import BackgroundTasks
from unittest.mock import MagicMock

from backend.services.order_service import order_service
from backend.core.utils.order_status_enums import OrderStatus
from backend.models.order import Order
from backend.schemas.order import OrderCreate, OrderItemCreate

@pytest.mark.asyncio
class TestOrderService:

    async def test_create_order_success(
            self,
            db_session,
            user_factory,
            product_factory
    ):
        
        user = await user_factory(email="testuser@example.com")

        product1 = await product_factory(name="Phone", price=1000, stock=10)
        product2 = await product_factory(name="Case", price=50, stock=5)

        order_in = OrderCreate(
            items=[
                OrderItemCreate(product_id=product1.id, quantity=2),
                OrderItemCreate(product_id=product2.id, quantity=1)
            ]
        )

        order = await order_service.create_order(db_session, order_in, user.id)

        assert order.user_id == user.id
        assert order.total_price == (1000 * 2) + (50 * 1)
        assert len(order.items) == 2

        await db_session.refresh(product1)
        await db_session.refresh(product2)

        assert product1.stock == 8
        assert product2.stock == 4

    async def test_create_order_insufficient_stock(
            self,
            db_session,
            user_factory,
            product_factory
    ):
        
        user = await user_factory(email="testuser@example.com")
        product = await product_factory(name="Limited Item", price=100, stock=2)

        order_in = OrderCreate(
            items=[OrderItemCreate(product_id=product.id, quantity=10)]
        )

        with pytest.raises(HTTPException) as excinfo:
            await order_service.create_order(db_session, order_in, user.id)

        assert excinfo.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Недостаточно товара" in excinfo.value.detail

    async def test_get_one_order_by_id_success(
            self,
            db_session,
            order_factory,
            user_factory
    ):
        user = await user_factory(email="testuser@example.com")

        order = await order_factory(user=user)

        order_found = await order_service.get_one_order_by_id(db_session, order.id, user)

        assert order_found is not None
        assert order_found.id == order.id

    async def test_get_one_order_by_id_error(
            self,
            db_session,
            user_factory
    ):
        
        user = await user_factory(email="testuser@example.com")

        with pytest.raises(HTTPException) as excinfo:
            await order_service.get_one_order_by_id(db_session, -1, user)

        assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND
        assert "Заказа под ID(-1) не найдено" in excinfo.value.detail

    async def test_edit_one_order_by_id_success(
            self,
            db_session,
            order_factory,
            user_factory,
    ):

        new_status = OrderStatus.COMPLETED    
        user = await user_factory(email="testuser@example.com")
        order = await order_factory(user=user)

        await order_service.edit_one_order_status_by_id(db_session, order.id, new_status)

        assert order.status == OrderStatus.COMPLETED

    async def test_edit_one_order_by_id_not_found(
            self,
            db_session
    ):
        
        with pytest.raises(HTTPException) as excinfo:
            await order_service.edit_one_order_status_by_id(db_session, -1, OrderStatus.COMPLETED)
        
        assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND
        assert "Заказа под ID(-1) не найдено" in excinfo.value.detail

    async def test_edit_one_order_by_id_status_error(
            self,
            db_session,
            order_factory,
            user_factory,
            product_factory
    ):

        user = await user_factory(email="testuser@example.com")

        product = await product_factory(name="Unique Test Product", price=100)
        products_data = [(product, 1)]

        order1 = await order_factory(user=user, status=OrderStatus.COMPLETED, products_data=products_data)

        with pytest.raises(HTTPException) as excinfo:
            await order_service.edit_one_order_status_by_id(db_session, order1.id, OrderStatus.CANCELLED)

        assert excinfo.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Нельзя изменить статус законченного заказа" in excinfo.value.detail

        order2 = await order_factory(user=user, status=OrderStatus.CANCELLED, products_data=products_data)

        with pytest.raises(HTTPException) as exc:
            await order_service.edit_one_order_status_by_id(db_session, order2.id, OrderStatus.COMPLETED)
        
        assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Нельзя изменить статус отмененного заказа" in exc.value.detail

        order3 = await order_factory(user=user, status=OrderStatus.SHIPPED, products_data=products_data)

        with pytest.raises(HTTPException) as exc2:
            await order_service.edit_one_order_status_by_id(db_session, order3.id, OrderStatus.CANCELLED)
        
        assert exc2.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Нельзя отменить заказ, который уже доставляется" in exc2.value.detail

    async def test_get_user_orders_history(
            self,
            db_session,
            user_factory,
            order_factory,
            product_factory
    ):
        
        user = await user_factory(email="testuser@example.com")

        product = await product_factory(name="Unique Product", price=100)
        products_data = [(product, 1)]

        order1 = await order_factory(user=user, status=OrderStatus.COMPLETED, products_data=products_data)
        order2 = await order_factory(user=user, status=OrderStatus.COMPLETED, products_data=products_data)
        order3 = await order_factory(user=user, status=OrderStatus.NEW, products_data=products_data)

        orders_history = await order_service.get_user_orders_history(db_session, current_user=user)

        assert len(orders_history) == 3

        orders_history_with_status_filter = await order_service.get_user_orders_history(
            db_session,
            current_user=user,
            status=OrderStatus.COMPLETED
        )

        assert len(orders_history_with_status_filter) == 2
        assert order3 not in orders_history_with_status_filter

        orders_history_with_status_filter_and_pagination = await order_service.get_user_orders_history(
            db_session,
            current_user=user,
            status=OrderStatus.COMPLETED,
            skip=1,
            limit=1
        )

        assert len(orders_history_with_status_filter_and_pagination) == 1
        assert order1 in orders_history_with_status_filter_and_pagination

    async def test_create_order_from_cart_success(
            self,
            db_session,
            user_factory,
            product_factory,
            cart_item_factory,
            mock_email_service
    ):
        
        user = await user_factory(email="testuser@example.com")
        product = await product_factory(name="Cart Item", price=500, stock=5)

        await cart_item_factory(user_id=user, product_id=product.id, quantity=2)

        bg_tasks = BackgroundTasks()
        bg_tasks.add_task = MagicMock()

        new_order = await order_service.create_order_from_cart(
            db=db_session,
            user_id=user.id,
            email=user.email,
            background_tasks=bg_tasks
        )

        assert new_order.total_price == 1000
        assert len(new_order.items) == 1

        from backend.crud.cart import cart_crud

        remaining_cart = await cart_crud.get_user_cart(db_session, user.id)

        assert len(remaining_cart) == 0

        bg_tasks.add_task.assert_called_once()

    async def test_create_order_from_cart_error(
            self,
            db_session,
            user_factory,
            product_factory,
            cart_item_factory
    ):
        
        user = await user_factory(email="testuser@example.com")
        product = await product_factory(name="Cart Item", price=500, stock=1)

        await cart_item_factory(user_id=user, product_id=product.id, quantity=2)

        bg_tasks = BackgroundTasks()
        bg_tasks.add_task = MagicMock()

        
        with pytest.raises(HTTPException) as exc:
            await order_service.create_order_from_cart(
                db=db_session,
                user_id=user.id,
                email=user.email,
                background_tasks=bg_tasks
            )
        
        assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Недостаточно товара" in exc.value.detail


    async def test_create_order_empty_cart(
            self,
            db_session,
            user_factory
    ):
        
        user = await user_factory(email="testuser@example.com")

        with pytest.raises(HTTPException) as excinfo:
            await order_service.create_order_from_cart(
                db_session,
                user.id,
                user.email,
                MagicMock()
            )

        assert excinfo.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Ваша корзина пуста" in excinfo.value.detail