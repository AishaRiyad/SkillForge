from httpx import AsyncClient


async def test_health_check_returns_healthy_status(
    client: AsyncClient,
) -> None:
    response = await client.get("/api/v1/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"
    assert data["service"] == "SkillForge API"
    assert data["version"] == "0.1.0"
    assert data["environment"] == "development"