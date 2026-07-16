from fastapi import APIRouter, status

from app.api.dependencies import DatabaseSession
from app.core.config import settings
from app.core.exceptions import ResourceNotFoundError
from app.services.database_service import DatabaseService

router = APIRouter(
    prefix="/health",
    tags=["Health"],
)


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    summary="Check API health",
)
async def health_check() -> dict[str, str]:
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.app_environment,
    }


@router.get(
    "/database",
    status_code=status.HTTP_200_OK,
    summary="Check database health",
)
async def database_health_check(
    session: DatabaseSession,
) -> dict[str, str]:
    is_connected = await DatabaseService.check_connection(session)

    return {
        "status": "healthy" if is_connected else "unhealthy",
        "database": "postgresql",
    }


@router.get(
    "/error-example",
    include_in_schema=False,
)
async def error_example() -> None:
    raise ResourceNotFoundError(
        resource="Example resource",
        resource_id="example-id",
    )
