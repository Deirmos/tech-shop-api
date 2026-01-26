import pytest
from sqlalchemy import select
from fastapi import HTTPException, status


from backend.services.user_service import user_service
from backend.crud.user import user_crud
from backend.schemas.user import UserRegister, UserLogin
from backend.models.user import User


@pytest.mark.asyncio
class TestUserService:

    async def test_register_user_success(self, db_session):
        user_data = UserRegister(
            email="test@example.com",
            username="testuser",
            password="strongpassword123"
        )

        new_user = await user_service.register_new_user(db_session, user_data)

        assert new_user.email == "test@example.com"
        assert new_user.username == "testuser"
        assert new_user.hashed_password != "strongpassword123"

        result = await db_session.execute(select(User).filter_by(email="test@example.com"))
        user_id_db = result.scalar_one_or_none()

        assert user_id_db is not None
        assert user_id_db.id == new_user.id

    
    async def test_register_user_duplicate_email(self, db_session, user_factory):
        await user_factory(email="exists@example.com")

        user_data = UserRegister(
            email="exists@example.com",
            username="newuser",
            password="password123"
        )

        with pytest.raises(HTTPException) as excinfo:
            await user_service.register_new_user(db_session, user_data)

        assert excinfo.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "пользователь с таким email уже существует" in excinfo.value.detail.lower()

    async def test_get_user_by_email(self, db_session, user_factory):

        created_user = await user_factory(email="findme@example.com")

        found_user = await user_crud.get_user_by_email(db_session, "findme@example.com")

        assert found_user is not None
        assert found_user.id == created_user.id
        assert found_user.email == "findme@example.com"

    async def test_get_user_by_email_not_found(self, db_session):
        found_user = await user_crud.get_user_by_email(db_session, "none@example.com")
        
        assert found_user is None

    async def test_login_user_success(self, db_session, user_factory):
        email = "login_test@example.com"
        password = "password123"

        await user_factory(email=email)

        login_data = UserLogin(email=email, password=password)

        result = await user_service.login_user(login_data, db_session)

        assert "access_token" in result
        assert result["token_type"] == "bearer"
        assert isinstance(result["access_token"], str)
    
    async def test_user_login_wrong_password(self, db_session, user_factory):

        email = "wrong_pass@example.com"

        await user_factory(email=email, password="correct_password")

        login_data = UserLogin(email=email, password="WRONG_password")

        with pytest.raises(HTTPException) as excinfo:
            await user_service.login_user(login_data, db_session)

        assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Неверный Email или пароль" in excinfo.value.detail

    async def test_login_user_not_found(self, db_session):

        login_data = UserLogin(email="nobody@example.com", password="anypassword")

        with pytest.raises(HTTPException) as excinfo:
            await user_service.login_user(login_data, db_session)

        assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED

        