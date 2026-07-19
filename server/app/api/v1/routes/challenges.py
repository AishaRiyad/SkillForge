from uuid import UUID

from fastapi import APIRouter, Response, status

from app.api.dependencies import (
    AdminUser,
    ChallengeServiceDependency,
)
from app.schemas.challenge import (
    ChallengeCreateRequest,
    ChallengeListResponse,
    ChallengeResponse,
    ChallengeUpdateRequest,
)

router = APIRouter(
    tags=["Challenges"],
)


@router.get(
    "/lessons/{lesson_id}/challenges",
    response_model=ChallengeListResponse,
)
async def list_lesson_challenges(
    lesson_id: UUID,
    challenge_service: ChallengeServiceDependency,
) -> ChallengeListResponse:
    return await challenge_service.list_public_challenges(lesson_id)


@router.get(
    "/challenges/{challenge_id}",
    response_model=ChallengeResponse,
)
async def get_challenge(
    challenge_id: UUID,
    challenge_service: ChallengeServiceDependency,
) -> ChallengeResponse:
    challenge = await challenge_service.get_public_challenge(challenge_id)

    return ChallengeResponse.model_validate(challenge)


@router.post(
    "/lessons/{lesson_id}/challenges",
    response_model=ChallengeResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_challenge(
    lesson_id: UUID,
    request: ChallengeCreateRequest,
    current_admin: AdminUser,
    challenge_service: ChallengeServiceDependency,
) -> ChallengeResponse:
    del current_admin

    challenge = await challenge_service.create_challenge(
        lesson_id,
        request,
    )

    return ChallengeResponse.model_validate(challenge)


@router.patch(
    "/challenges/{challenge_id}",
    response_model=ChallengeResponse,
)
async def update_challenge(
    challenge_id: UUID,
    request: ChallengeUpdateRequest,
    current_admin: AdminUser,
    challenge_service: ChallengeServiceDependency,
) -> ChallengeResponse:
    del current_admin

    challenge = await challenge_service.update_challenge(
        challenge_id,
        request,
    )

    return ChallengeResponse.model_validate(challenge)


@router.delete(
    "/challenges/{challenge_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_challenge(
    challenge_id: UUID,
    current_admin: AdminUser,
    challenge_service: ChallengeServiceDependency,
) -> Response:
    del current_admin

    await challenge_service.delete_challenge(challenge_id)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
