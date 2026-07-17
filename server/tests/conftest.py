from collections.abc import AsyncIterator, Iterator

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.main import create_application


@pytest.fixture
def application() -> FastAPI:
    return create_application()


@pytest.fixture
async def client(
    application: FastAPI,
) -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=application)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as async_client:
        yield async_client


@pytest.fixture(autouse=True)
def clear_dependency_overrides(
    application: FastAPI,
) -> Iterator[None]:
    yield
    application.dependency_overrides.clear()
