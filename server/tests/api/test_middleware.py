from uuid import UUID

from httpx import AsyncClient


async def test_response_contains_generated_request_id(
    client: AsyncClient,
) -> None:
    response = await client.get("/")

    assert response.status_code == 200
    assert "X-Request-ID" in response.headers

    request_id = response.headers["X-Request-ID"]

    assert str(UUID(request_id)) == request_id


async def test_response_preserves_client_request_id(
    client: AsyncClient,
) -> None:
    request_id = "skillforge-test-request"

    response = await client.get(
        "/",
        headers={"X-Request-ID": request_id},
    )

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == request_id


async def test_response_contains_process_time(
    client: AsyncClient,
) -> None:
    response = await client.get("/")

    assert response.status_code == 200
    assert "X-Process-Time" in response.headers
    assert float(response.headers["X-Process-Time"]) >= 0
