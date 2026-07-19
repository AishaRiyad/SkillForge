from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.challenge import Challenge
from app.models.enums import ChallengeStatus


class ChallengeRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        *,
        lesson_id: UUID,
        title: str,
        description: str | None,
        passing_score: int,
        xp_reward: int,
        max_attempts: int | None,
        status: ChallengeStatus,
    ) -> Challenge:
        challenge = Challenge(
            lesson_id=lesson_id,
            title=title,
            description=description,
            passing_score=passing_score,
            xp_reward=xp_reward,
            max_attempts=max_attempts,
            status=status,
            is_active=True,
        )

        self.session.add(challenge)
        await self.session.flush()

        return challenge

    async def get_by_id(
        self,
        challenge_id: UUID,
        *,
        include_inactive: bool = False,
        include_unpublished: bool = False,
    ) -> Challenge | None:
        statement = select(Challenge).where(Challenge.id == challenge_id)

        if not include_inactive:
            statement = statement.where(Challenge.is_active.is_(True))

        if not include_unpublished:
            statement = statement.where(Challenge.status == ChallengeStatus.PUBLISHED)

        result = await self.session.execute(statement)

        return result.scalar_one_or_none()

    async def list_by_lesson(
        self,
        lesson_id: UUID,
        *,
        include_inactive: bool = False,
        include_unpublished: bool = False,
    ) -> list[Challenge]:
        statement = select(Challenge).where(Challenge.lesson_id == lesson_id)

        if not include_inactive:
            statement = statement.where(Challenge.is_active.is_(True))

        if not include_unpublished:
            statement = statement.where(Challenge.status == ChallengeStatus.PUBLISHED)

        statement = statement.order_by(Challenge.created_at.asc())

        result = await self.session.execute(statement)

        return list(result.scalars().all())

    async def count_by_lesson(
        self,
        lesson_id: UUID,
        *,
        include_inactive: bool = False,
        include_unpublished: bool = False,
    ) -> int:
        statement = select(func.count(Challenge.id)).where(
            Challenge.lesson_id == lesson_id
        )

        if not include_inactive:
            statement = statement.where(Challenge.is_active.is_(True))

        if not include_unpublished:
            statement = statement.where(Challenge.status == ChallengeStatus.PUBLISHED)

        result = await self.session.execute(statement)

        return int(result.scalar_one())

    async def update(
        self,
        challenge: Challenge,
        update_data: dict[str, Any],
    ) -> Challenge:
        for field_name, value in update_data.items():
            setattr(challenge, field_name, value)

        await self.session.flush()

        return challenge

    async def soft_delete(
        self,
        challenge: Challenge,
    ) -> Challenge:
        challenge.is_active = False
        challenge.status = ChallengeStatus.ARCHIVED

        await self.session.flush()

        return challenge
