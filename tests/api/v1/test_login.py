import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_get_access_token(client: AsyncClient) -> None:
    # 1. Create a User first
    register_data = {
        "email": "test@example.com",
        "password": "testpassword",
        "full_name": "Test User"
    }
    response = await client.post("/api/v1/users/", json=register_data)
    assert response.status_code == 200
    
    # 2. Try to Login
    login_data = {
        "username": "test@example.com",
        "password": "testpassword"
    }
    response = await client.post("/api/v1/login/access-token", data=login_data)
    assert response.status_code == 200
    tokens = response.json()
    assert "access_token" in tokens
    assert tokens["token_type"] == "bearer"
