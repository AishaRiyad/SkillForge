from fastapi import APIRouter, Response, status

from app.api.dependencies import (
    ActiveUser,
    AuthServiceDependency,
)
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    LogoutAllResponse,
    LogoutRequest,
    RefreshTokenRequest,
    TokenPair,
)
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


@router.post(
    "/refresh",
    response_model=TokenPair,
    status_code=status.HTTP_200_OK,
    summary="Rotate a refresh token",
)
async def refresh_tokens(
    refresh_data: RefreshTokenRequest,
    auth_service: AuthServiceDependency,
) -> TokenPair:
    return await auth_service.refresh_tokens(refresh_data.refresh_token)


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Log out the current session",
)
async def logout(
    logout_data: LogoutRequest,
    auth_service: AuthServiceDependency,
) -> Response:
    await auth_service.logout(logout_data.refresh_token)

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/logout-all",
    response_model=LogoutAllResponse,
    status_code=status.HTTP_200_OK,
    summary="Log out from all sessions",
)
async def logout_all(
    current_user: ActiveUser,
    auth_service: AuthServiceDependency,
) -> LogoutAllResponse:
    revoked_sessions = await auth_service.logout_all(current_user)

    return LogoutAllResponse(
        message="All refresh-token sessions were revoked.",
        revoked_sessions=revoked_sessions,
    )
