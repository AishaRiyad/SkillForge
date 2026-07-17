from fastapi import APIRouter, status

from app.api.dependencies import (
    ActiveUser,
    UserServiceDependency,
)
from app.schemas.user import (
    ProfileResponse,
    ProfileUpdateRequest,
    UserResponse,
)

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get the authenticated user",
)
async def get_my_profile(
    current_user: ActiveUser,
) -> UserResponse:
    return UserResponse.model_validate(current_user)


@router.patch(
    "/me/profile",
    response_model=ProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Update the authenticated user's profile",
)
async def update_my_profile(
    update_request: ProfileUpdateRequest,
    current_user: ActiveUser,
    user_service: UserServiceDependency,
) -> ProfileResponse:
    profile = await user_service.update_profile(
        current_user,
        update_request,
    )

    return ProfileResponse.model_validate(profile)
