from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.profile import Profile
from app.models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(
        self,
        user_id: UUID,
    ) -> User | None:
        statement = (
            select(User).options(selectinload(User.profile)).where(User.id == user_id)
        )

        result = await self.session.execute(statement)

        return result.scalar_one_or_none()

    async def get_by_email(
        self,
        email: str,
    ) -> User | None:
        normalized_email = email.strip().lower()

        statement = (
            select(User)
            .options(selectinload(User.profile))
            .where(func.lower(User.email) == normalized_email)
        )

        result = await self.session.execute(statement)

        return result.scalar_one_or_none()

    async def get_by_username(
        self,
        username: str,
    ) -> User | None:
        normalized_username = username.strip().lower()

        statement = (
            select(User)
            .join(User.profile)
            .where(func.lower(Profile.username) == normalized_username)
        )

        result = await self.session.execute(statement)

        return result.scalar_one_or_none()

    async def create(
        self,
        *,
        email: str,
        hashed_password: str,
        username: str,
        display_name: str,
    ) -> User:
        user = User(
            email=email.strip().lower(),
            hashed_password=hashed_password,
        )

        user.profile = Profile(
            username=username.strip().lower(),
            display_name=display_name.strip(),
        )

        self.session.add(user)
        await self.session.flush()

        return user
