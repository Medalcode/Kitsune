from typing import Optional, Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app import models, schemas
from src.app.core.security import get_password_hash


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_email(self, email: str) -> Optional[models.User]:
        result = await self.db.execute(select(models.User).filter(models.User.email == email))
        return result.scalars().first()

    async def create(self, user_in: schemas.UserCreate) -> models.User:
        user = models.User(
            email=user_in.email,
            full_name=user_in.full_name,
            hashed_password=get_password_hash(user_in.password),
            is_active=user_in.is_active,
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def get_multi(self, skip: int = 0, limit: int = 100) -> tuple[Sequence[models.User], int]:
        # Get items
        query = select(models.User).offset(skip).limit(limit)
        result = await self.db.execute(query)
        items = result.scalars().all()

        # Get total
        count_query = select(func.count()).select_from(models.User)
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        return items, total
