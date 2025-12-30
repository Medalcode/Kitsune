from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.app.db.session import get_db
from src.app import models, schemas

router = APIRouter()

@router.get("/", response_model=List[schemas.User])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Retrieve users.
    """
    result = await db.execute(select(models.User).offset(skip).limit(limit))
    users = result.scalars().all()
    return users

@router.post("/", response_model=schemas.User)
async def create_user(
    user_in: schemas.UserCreate,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Create new user.
    """
    # Check if user exists
    result = await db.execute(select(models.User).filter(models.User.email == user_in.email))
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    
    new_user = models.User(
        email=user_in.email,
        full_name=user_in.full_name,
        is_active=user_in.is_active
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user
