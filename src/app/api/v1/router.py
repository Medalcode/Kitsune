from fastapi import APIRouter

api_router = APIRouter()

from src.app.api.v1.endpoints import users

api_router.include_router(users.router, prefix="/users", tags=["users"])

@api_router.get("/health", tags=["system"])
async def health_check():
    return {"status": "ok", "message": "System is healthy"}
