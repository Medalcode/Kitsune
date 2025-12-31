from typing import Generic, Sequence, TypeVar
from pydantic import BaseModel
from fastapi import Query

T = TypeVar("T")

class Params(BaseModel):
    page: int = Query(1, ge=1, description="Page number")
    size: int = Query(50, ge=1, le=100, description="Page size")

class Page(BaseModel, Generic[T]):
    items: Sequence[T]
    total: int
    page: int
    size: int
    pages: int

def paginate(items: Sequence[T], params: Params) -> Page[T]:
    # Nota: Esta es una paginación en memoria simple. 
    # Para producción con SQL, se debe hacer a nivel de query.
    # Aquí asumimos que 'items' ya viene paginado o es una lista completa.
    # Si viene completa (SQLAlchemy .all()), hacemos slice.
    # Si ya viene paginada desde DB, solo envolvemos.
    
    # En este template, modificaremos las queries para usar offset/limit basados en params
    pass
