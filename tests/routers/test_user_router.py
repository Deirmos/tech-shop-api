import pytest
from fastapi import HTTPException, status

@pytest.mark.asyncio
class TestUserRouter:

    async def test_register_user_success(
            self,
            async_client,
            db_session
    ):
        
        payload = {
            "email": "router_test@example.com",
            "username": "router_user",
            "password": "strongpassword"
        }

        response = await async_client.post("/api/user/register", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == payload["email"]
        assert "id" in data
        assert "hashed_password" not in data

    async def test_register_user_duplicate_email(
            self,
            async_client,
            user
    ):
        
        payload = {
            "email": user.email,
            "username": "another_user",
            "password": "somepassword"
        }

        response = await async_client.post("/api/user/register", json=payload)

        assert response.status_code == 400
        assert response.json()["detail"] == "Пользователь с таким Email уже существует"

    async def test_register_user_invalid_email(
            self,
            async_client
    ):
        
        payload = {
            "email": "not-an-email",
            "username": "test_user",
            "password": "password123"
        }

        response = await async_client.post("/api/user/register", json=payload)

        assert response.status_code == 422
        assert response.json()["detail"][0]["loc"] == ["body", "email"]

    async def test_register_user_missing_fields(
            self,
            async_client
    ):
        
        payload = {}

        response = await async_client.post("/api/user/register", json=payload)

        assert response.status_code == 422

    async def test_login_success(
            self,
            async_client,
            user_factory
    ):
        
        await user_factory(email="login@test.com")

        login_data = {
            "username": "login@test.com",
            "password": "password123"
        }

        response = await async_client.post("/api/user/login", data=login_data)

        assert response.status_code == 200
        token_data = response.json()
        assert "access_token" in token_data
        assert token_data["token_type"] == "bearer"

    async def test_login_user_wrong_email_or_password(
            self,
            async_client,
    ):
        
        login_data = {
            "username": "usernotfound@example.com",
            "password": "password123"
        }

        response = await async_client.post("/api/user/login", data=login_data)

        assert response.status_code == 401
        assert response.json()["detail"] == "Неверный Email или пароль"
    