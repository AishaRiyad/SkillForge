from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ResourceNotFoundError
from app.models.challenge import Challenge
from app.repositories.challenge_repository import ChallengeRepository
from app.repositories.lesson_repository import LessonRepository
from app.schemas.challenge import (
    ChallengeCreateRequest,
    ChallengeListResponse,
    ChallengeResponse,
    ChallengeUpdateRequest,
)


class ChallengeService:
    def __init__(
        self,
        session: AsyncSession,
        challenge_repository: ChallengeRepository,
        lesson_repository: LessonRepository,
    ) -> None:
        self.session = session
        self.challenge_repository = challenge_repository
        self.lesson_repository = lesson_repository

    async def create_challenge(
        self,
        lesson_id: UUID,
        request: ChallengeCreateRequest,
    ) -> Challenge:
        await self._ensure_lesson_exists(lesson_id)

        try:
            challenge = await self.challenge_repository.create(
                lesson_id=lesson_id,
                title=request.title,
                description=request.description,
                passing_score=request.passing_score,
                xp_reward=request.xp_reward,
                max_attempts=request.max_attempts,
                status=request.status,
            )

            await self.session.commit()
            await self.session.refresh(challenge)

            return challenge

        except Exception:
            await self.session.rollback()
            raise

    async def get_public_challenge(
        self,
        challenge_id: UUID,
    ) -> Challenge:
        challenge = await self.challenge_repository.get_by_id(challenge_id)

        if challenge is None:
            raise ResourceNotFoundError(
                resource="Challenge",
                resource_id=str(challenge_id),
            )

        return challenge

    async def get_managed_challenge(
        self,
        challenge_id: UUID,
    ) -> Challenge:
        challenge = await self.challenge_repository.get_by_id(
            challenge_id,
            include_inactive=True,
            include_unpublished=True,
        )

        if challenge is None:
            raise ResourceNotFoundError(
                resource="Challenge",
                resource_id=str(challenge_id),
            )

        return challenge

    async def list_public_challenges(
        self,
        lesson_id: UUID,
    ) -> ChallengeListResponse:
        await self._ensure_lesson_exists(lesson_id)

        challenges = await self.challenge_repository.list_by_lesson(lesson_id)

        total = await self.challenge_repository.count_by_lesson(lesson_id)

        return ChallengeListResponse(
            items=[
                ChallengeResponse.model_validate(challenge) for challenge in challenges
            ],
            total=total,
        )

    async def update_challenge(
        self,
        challenge_id: UUID,
        request: ChallengeUpdateRequest,
    ) -> Challenge:
        challenge = await self.get_managed_challenge(challenge_id)

        update_data = request.model_dump(exclude_unset=True)

        if not update_data:
            return challenge

        try:
            updated_challenge = await self.challenge_repository.update(
                challenge,
                update_data,
            )

            await self.session.commit()
            await self.session.refresh(updated_challenge)

            return updated_challenge

        except Exception:
            await self.session.rollback()
            raise

    async def delete_challenge(
        self,
        challenge_id: UUID,
    ) -> None:
        challenge = await self.get_managed_challenge(challenge_id)

        if not challenge.is_active:
            return

        try:
            await self.challenge_repository.soft_delete(challenge)

            await self.session.commit()

        except Exception:
            await self.session.rollback()
            raise

    async def _ensure_lesson_exists(
        self,
        lesson_id: UUID,
    ) -> None:
        lesson = await self.lesson_repository.get_by_id(
            lesson_id,
            include_inactive=False,
            include_unpublished=True,
        )

        if lesson is None:
            raise ResourceNotFoundError(
                resource="Active lesson",
                resource_id=str(lesson_id),
            )
