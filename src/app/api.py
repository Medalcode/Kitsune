from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.app import models, schemas
from src.app.core import settings, security, verify_password, create_access_token
from src.app.database import get_db
from src.app.logic import UserLogic

# --- DEPENDENCIES ---
reusable_oauth2 = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/login/access-token")

async def get_current_user(db: AsyncSession = Depends(get_db), token: str = Depends(reusable_oauth2)) -> models.User:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        token_data = schemas.TokenPayload(**payload)
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        ) from None
    result = await db.execute(select(models.User).filter(models.User.id == int(token_data.sub)))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

async def get_current_active_user(current_user: models.User = Depends(get_current_user)) -> models.User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# --- ENDPOINTS ---
router = APIRouter()

@router.get("/health", tags=["system"])
async def health_check():
    return {"status": "ok", "message": "System is healthy"}

@router.post("/login/access-token", response_model=schemas.Token, tags=["login"])
async def login_access_token(
    db: AsyncSession = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    logic = UserLogic(db)
    user = await logic.get_by_email(form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": create_access_token(subject=user.id, expires_delta=access_token_expires),
        "token_type": "bearer",
    }

@router.get("/users/", response_model=schemas.Page[schemas.User], tags=["users"])
async def read_users(
    page: int = 1,
    size: int = 50,
    current_user: models.User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    skip = (page - 1) * size
    logic = UserLogic(db)
    items, total = await logic.get_multi(skip=skip, limit=size)
    return {"items": items, "total": total, "page": page, "size": size, "pages": (total + size - 1) // size}

@router.post("/users/", response_model=schemas.User, tags=["users"])
async def create_user(
    user_in: schemas.UserCreate,
    db: AsyncSession = Depends(get_db),
) -> Any:
    logic = UserLogic(db)
    if await logic.get_by_email(user_in.email):
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    return await logic.create(user_in)
