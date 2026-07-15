from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    print(f"Starting {settings.app_name}")
    yield
    print(f"Stopping {settings.app_name}")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Gamified learning and skill development platform API."
    ),
    debug=settings.app_debug,
    lifespan=lifespan,
)

app.include_router(api_router)


@app.get(
    "/",
    tags=["Root"],
    summary="Get API information",
)
async def root() -> dict[str, str]:
    return {
        "message": "Welcome to SkillForge API",
        "documentation": "/docs",
        "health": f"{settings.api_v1_prefix}/health",
    }