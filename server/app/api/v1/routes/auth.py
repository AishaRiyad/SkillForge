from fastapi import APIRouter, status

from app.api.dependencies import AuthServiceDependency
from app.schemas.auth import LoginRequest, LoginResponse
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


@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    summary="Authenticate a user",
)
async def login_user(
    login_data: LoginRequest,
    auth_service: AuthServiceDependency,
) -> LoginResponse:
    return await auth_service.login_user(login_data)
