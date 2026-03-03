from typing import Generic, Optional, Sequence, TypeVar

from fastapi import Query
from pydantic import BaseModel, ConfigDict, EmailStr

T = TypeVar("T")

# --- COMMON ---
class Params(BaseModel):
    page: int = Query(1, ge=1, description="Page number")
    size: int = Query(50, ge=1, le=100, description="Page size")


class Page(BaseModel, Generic[T]):
    items: Sequence[T]
    total: int
    page: int
    size: int
    pages: int

# --- TOKEN ---
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    sub: Optional[str] = None

# --- USER ---
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    is_active: Optional[bool] = True


class UserCreate(UserBase):
    password: str


class UserUpdate(UserBase):
    pass


class UserInDBBase(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class User(UserInDBBase):
    pass
