from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.profile import Profile


class ProfileRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_user_id(
        self,
        user_id: UUID,
    ) -> Profile | None:
        statement = select(Profile).where(Profile.user_id == user_id)

        result = await self.session.execute(statement)

        return result.scalar_one_or_none()

    async def get_by_username(
        self,
        username: str,
    ) -> Profile | None:
        normalized_username = username.strip().lower()

        statement = select(Profile).where(
            func.lower(Profile.username) == normalized_username
        )

        result = await self.session.execute(statement)

        return result.scalar_one_or_none()

    async def update(
        self,
        profile: Profile,
        update_data: dict[str, Any],
    ) -> Profile:
        for field_name, value in update_data.items():
            setattr(profile, field_name, value)

        await self.session.flush()

        return profile
