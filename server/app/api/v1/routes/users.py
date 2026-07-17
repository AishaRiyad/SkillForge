from fastapi import APIRouter, status

from app.api.dependencies import ActiveUser
from app.schemas.user import UserResponse

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
