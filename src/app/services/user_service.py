from typing import Optional, Sequence
from sqlalchemy.ext.asyncio import AsyncSession

from src.app import models, schemas
from src.app.core.security import get_password_hash
from src.app.repositories.user_repository import UserRepository

class UserService:
    def __init__(self, db: AsyncSession):
        self.repository = UserRepository(db)

    async def get_by_email(self, email: str) -> Optional[models.User]:
        return await self.repository.get_by_email(email)

    async def create(self, user_in: schemas.UserCreate) -> models.User:
        user_data = user_in.model_dump()
        user_data["hashed_password"] = get_password_hash(user_in.password)
        del user_data["password"]
        
        return await self.repository.create(user_data)

    async def get_multi(self, skip: int = 0, limit: int = 100) -> tuple[Sequence[models.User], int]:
        items = await self.repository.get_all(skip=skip, limit=limit)
        total = await self.repository.count()
        return items, total
