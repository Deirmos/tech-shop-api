import pytest

from backend.core.utils.order_status_enums import OrderStatus

@pytest.mark.asyncio
class TestOrderRouter:

    async def test_get_orders_history_success(
            self,
            auth_client,
            user,
            order_factory
    ):
        
        order1 = await order_factory(user=user, status=OrderStatus.NEW)
        order2 = await order_factory(user=user, status=OrderStatus.COMPLETED)

        response = await auth_client.get("/api/order/history")

        assert response.status_code == 200

        data = response.json()
        assert len(data) == 2

        returned_ids = {order["id"] for order in data}
        
        assert order1.id in returned_ids
        assert order2.id in returned_ids

    async def test_get_orders_history_filtered_by_status(
            self,
            auth_client,
            user,
            order_factory
    ):
        
        await order_factory(user=user, status=OrderStatus.NEW)

        completed = await order_factory(
            user=user,
            status=OrderStatus.COMPLETED
        )

        response = await auth_client.get(
            "/api/order/history",
            params={"status": OrderStatus.COMPLETED.value}
        )

        assert response.status_code == 200

        data = response.json()

        assert len(data) == 1
        assert data[0]["id"] == completed.id
        assert data[0]["status"] == OrderStatus.COMPLETED.value

    async def test_get_orders_history_pagination(
            self,
            auth_client,
            user,
            order_factory
    ):
        order1 = await order_factory(user=user)
        order2 = await order_factory(user=user)
        order3 = await order_factory(user=user)

        response = await auth_client.get(
            "/api/order/history",
            params={"skip": 1, "limit": 1}
        )

        assert response.status_code == 200

        data = response.json()

        assert len(data) == 1
        assert data[0]["id"] == order2.id

    async def test_get_order_by_id_found(
            self,
            auth_client,
            user,
            order_factory
    ):
        order1 = await order_factory(user=user)
        order2 = await order_factory(user=user)

        response = await auth_client.get(f"/api/order/{order1.id}")

        assert response.status_code == 200

        data = response.json()

        assert data["id"] == order1.id

    async def test_get_order_by_id_not_found(
            self,
            auth_client,
    ):
        response = await auth_client.get(f"/api/order/{-1}")

        assert response.status_code == 404

    async def test_edit_order_status_by_id_success(
            self,
            admin_client,
            order_factory
    ):
        order = await order_factory()

        new_status = OrderStatus.COMPLETED

        response = await admin_client.put(
            f"/api/admin/order/status/{order.id}",
            params={"new_status": new_status.value}
        )

        assert response.status_code == 200

        data = response.json()

        assert data["id"] == order.id
        assert data["status"] == new_status.value

    async def test_edit_order_status_by_id_not_found(
            self,
            admin_client
    ):
        
        new_status = OrderStatus.COMPLETED
        
        response = await admin_client.put(
            f"/api/admin/order/status/{-1}",
            params={"new_status": new_status.value}
        )

        assert response.status_code == 404

    async def test_edit_order_status_wrong_new_status(
            self,
            admin_client,
            order_factory
    ):
        
        order = await order_factory(status=OrderStatus.COMPLETED)

        new_status = OrderStatus.CANCELLED

        response = await admin_client.put(
            f"/api/admin/order/status/{order.id}",
            params={"new_status": new_status.value}
        )

        assert response.status_code == 400

    