from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    ConflictError,
    ResourceNotFoundError,
)
from app.models.profile import Profile
from app.models.user import User
from app.repositories.profile_repository import ProfileRepository
from app.schemas.user import ProfileUpdateRequest


class UserService:
    def __init__(
        self,
        session: AsyncSession,
        profile_repository: ProfileRepository,
    ) -> None:
        self.session = session
        self.profile_repository = profile_repository

    async def update_profile(
        self,
        user: User,
        update_request: ProfileUpdateRequest,
    ) -> Profile:
        profile = await self.profile_repository.get_by_user_id(user.id)

        if profile is None:
            raise ResourceNotFoundError(
                resource="User profile",
                resource_id=str(user.id),
            )

        update_data = update_request.model_dump(exclude_unset=True)

        if not update_data:
            return profile

        requested_username = update_data.get("username")

        if requested_username is not None and requested_username != profile.username:
            existing_profile = await self.profile_repository.get_by_username(
                requested_username
            )

            if existing_profile is not None and existing_profile.user_id != user.id:
                raise ConflictError(
                    message="This username is already in use.",
                    details={"field": "username"},
                )

        try:
            updated_profile = await self.profile_repository.update(
                profile,
                update_data,
            )

            await self.session.commit()
            await self.session.refresh(updated_profile)

            return updated_profile

        except IntegrityError as exception:
            await self.session.rollback()

            raise ConflictError(
                message="This username is already in use.",
                details={"field": "username"},
            ) from exception

        except Exception:
            await self.session.rollback()
            raise
