from httpx import AsyncClient


async def test_root_returns_api_information(client: AsyncClient) -> None:
    response = await client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data == {
        "message": "Welcome to SkillForge API",
        "documentation": "/docs",
        "health": "/api/v1/health",
    }
