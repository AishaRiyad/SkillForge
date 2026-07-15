from httpx import AsyncClient


async def test_custom_application_error_has_standard_format(
    client: AsyncClient,
) -> None:
    response = await client.get("/api/v1/health/error-example")

    assert response.status_code == 404

    data = response.json()

    assert data["error"] == {
        "code": "RESOURCE_NOT_FOUND",
        "message": "Example resource was not found.",
        "details": {
            "resource": "Example resource",
            "resource_id": "example-id",
        },
    }

    assert data["request_id"] == response.headers["X-Request-ID"]


async def test_unknown_route_has_standard_error_format(
    client: AsyncClient,
) -> None:
    response = await client.get("/api/v1/does-not-exist")

    assert response.status_code == 404

    data = response.json()

    assert data["error"]["code"] == "HTTP_ERROR"
    assert data["error"]["message"] == "Not Found"
    assert data["error"]["details"] is None
    assert data["request_id"] == response.headers["X-Request-ID"]
