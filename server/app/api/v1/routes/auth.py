from fastapi import APIRouter, status

from app.api.dependencies import AuthServiceDependency
from app.schemas.user import (
    UserRegistrationRequest,
    UserResponse,
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
async def register_user(
    registration_data: UserRegistrationRequest,
    auth_service: AuthServiceDependency,
) -> UserResponse:
    user = await auth_service.register_user(registration_data)

    return UserResponse.model_validate(user)
