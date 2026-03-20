from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from datetime import timedelta
from fastapi.security import OAuth2PasswordBearer

from backend.crud.user import user_crud
from backend.schemas.user import UserRegister, UserLogin
from backend.core.utils.security import hash_password
from backend.core.database import get_db
from backend.models.user import User

from backend.core.exceptions.auth_exceptions import *

from backend.core.utils.security import (
    verify_password,
    verify_access_token,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/user/login")


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: AsyncSession = Depends(get_db)
) -> User:

    payload = verify_access_token(token)
    if payload is None:
        raise InvalidCredentialsError()
        
    user_id_str: str = payload.get("sub")
    if user_id_str is None:
        raise InvalidCredentialsError()
        
    try:
        user_id_int = int(user_id_str)
    except (ValueError, TypeError):
        raise InvalidCredentialsError()
        
    user = await user_crud.get_user_by_id(db, user_id_int)

    if user is None:
        raise InvalidCredentialsError()
        
    return user

async def get_current_admin_user(
        current_user: User = Depends(get_current_user)
    ) -> User:
        if not current_user.is_admin:
            raise AuthorizationError()
        return current_user

class UserService:

    @staticmethod
    async def register_new_user(
        db: AsyncSession,
        user_data: UserRegister
    ):
        
        existing_user = await user_crud.get_user_by_email(db, user_data.email)

        if existing_user:
            raise UserAlreadyExistsError()
        
        hashed_pw = hash_password(user_data.password)

        user_create_data = user_data.model_dump()
        user_create_data["hashed_password"] = hashed_pw
        del user_create_data["password"]

        user = await user_crud.create_user(db, user_create_data)
    
        await db.commit()
        await db.refresh(user)

        return user
    
    @staticmethod
    async def login_user(
        user_data: UserLogin,
        db: AsyncSession
    ):
        
        login_id = getattr(user_data, "email", None) or getattr(user_data, "username", None)

        if not login_id:
            raise UserDataNotFoundError()
        
        user = await user_crud.get_user_by_email(db, login_id)

        if not user or not verify_password(user_data.password, user.hashed_password):
            raise InvalidCredentialsError()
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email},
            expire_delta=access_token_expires
        )

        return {
            "access_token": access_token,
            "token_type": "bearer"
        }

user_service = UserService()