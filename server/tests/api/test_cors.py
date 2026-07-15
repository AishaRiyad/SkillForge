from httpx import AsyncClient


async def test_allowed_origin_receives_cors_headers(
    client: AsyncClient,
) -> None:
    response = await client.options(
        "/api/v1/health",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"
    assert response.headers["access-control-allow-credentials"] == "true"


async def test_unknown_origin_is_not_allowed(
    client: AsyncClient,
) -> None:
    response = await client.options(
        "/api/v1/health",
        headers={
            "Origin": "https://untrusted.example",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert "access-control-allow-origin" not in response.headers


async def test_custom_headers_are_exposed(
    client: AsyncClient,
) -> None:
    response = await client.get(
        "/api/v1/health",
        headers={"Origin": "http://localhost:5173"},
    )

    exposed_headers = response.headers["access-control-expose-headers"]

    assert "X-Request-ID" in exposed_headers
    assert "X-Process-Time" in exposed_headers
