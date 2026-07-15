from fastapi import APIRouter, status

from app.core.config import settings

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