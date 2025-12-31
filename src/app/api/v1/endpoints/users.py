from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.app.db.session import get_db
from src.app import models, schemas
from src.app.core.security import get_password_hash

router = APIRouter()

from src.app.api import deps

from src.app.schemas.common import Page
from sqlalchemy import func

@router.get("/", response_model=Page[schemas.User])
async def read_users(
    page: int = 1,
    size: int = 50,
    current_user: models.User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Retrieve users with pagination.
    """
    skip = (page - 1) * size
    
    # Get total count
    count_query = select(func.count()).select_from(models.User)
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Get items
    query = select(models.User).offset(skip).limit(size)
    result = await db.execute(query)
    users = result.scalars().all()
    
    return {
        "items": users,
        "total": total,
        "page": page,
        "size": size,
        "pages": (total + size - 1) // size
    }

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
        hashed_password=get_password_hash(user_in.password),
        is_active=user_in.is_active
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user
