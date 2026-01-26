from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm

from backend.schemas.user import UserResponse, UserRegister, UserLogin, Token
from backend.services.user_service import user_service
from backend.core.database import get_db

router = APIRouter(prefix="/user", tags=["users"])

@router.post("/register", response_model=UserResponse)
async def register_user(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db)
):
    
    user = await user_service.register_new_user(db, user_data)

    return user

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    
    token = await user_service.login_user(
        user_data=form_data,
        db=db
    )

    return token