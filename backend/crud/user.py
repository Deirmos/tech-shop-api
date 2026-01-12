from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.models.user import User
from backend.schemas.user import UserRegister
from backend.core.utils.security import hash_password

class UserCRUD:

    @staticmethod
    async def get_user_by_id(
        db: AsyncSession,
        user_id: int
    ) -> User | None:
        
        user = await db.execute(select(User).where(User.id == user_id))

        return user.scalar_one_or_none()
    
    @staticmethod
    async def get_user_by_email(
        db: AsyncSession,
        user_email: str
    ) -> User | None:
        
        user = await db.execute(select(User).where(User.email == user_email))

        return user.scalar_one_or_none()
    
    @staticmethod
    async def create_user(
        db: AsyncSession,
        user_data_dict: dict
    ):
        
        user = User(**user_data_dict)

        db.add(user)
        await db.flush()
        return user

user_crud = UserCRUD()