from typing import Generic, List, Optional, Sequence, Type, TypeVar

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.core import get_password_hash
from src.app.database import Base
from src.app.models import User
from src.app.schemas import UserCreate

ModelType = TypeVar("ModelType", bound=Base)

class CRUD(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db

    async def get(self, id: int) -> Optional[ModelType]:
        query = select(self.model).filter(self.model.id == id)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        query = select(self.model).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def create(self, obj_in: dict) -> ModelType:
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def count(self) -> int:
        query = select(func.count()).select_from(self.model)
        result = await self.db.execute(query)
        return result.scalar() or 0

class UserLogic:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.crud = CRUD(User, db)

    async def get_by_email(self, email: str) -> Optional[User]:
        query = select(User).filter(User.email == email)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def create(self, user_in: UserCreate) -> User:
        user_data = user_in.model_dump()
        user_data["hashed_password"] = get_password_hash(user_in.password)
        del user_data["password"]
        return await self.crud.create(user_data)

    async def get_multi(self, skip: int = 0, limit: int = 100) -> tuple[Sequence[User], int]:
        items = await self.crud.get_all(skip=skip, limit=limit)
        total = await self.crud.count()
        return items, total
