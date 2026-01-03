from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.app import models, schemas
from src.app.api import deps
from src.app.db.session import get_db
from src.app.schemas.common import Page
from src.app.services.user_service import UserService

router = APIRouter()


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
    service = UserService(db)
    items, total = await service.get_multi(skip=skip, limit=size)

    return {"items": items, "total": total, "page": page, "size": size, "pages": (total + size - 1) // size}


@router.post("/", response_model=schemas.User)
async def create_user(
    user_in: schemas.UserCreate,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Create new user.
    """
    service = UserService(db)

    # Check if user exists
    if await service.get_by_email(user_in.email):
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )

    return await service.create(user_in)
