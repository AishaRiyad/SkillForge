from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError
from app.core.security import hash_password
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserRegistrationRequest


class AuthService:
    def __init__(
        self,
        session: AsyncSession,
        user_repository: UserRepository,
    ) -> None:
        self.session = session
        self.user_repository = user_repository

    async def register_user(
        self,
        registration_data: UserRegistrationRequest,
    ) -> User:
        existing_email_user = await self.user_repository.get_by_email(
            str(registration_data.email)
        )

        if existing_email_user is not None:
            raise ConflictError(
                message="An account with this email already exists.",
                details={"field": "email"},
            )

        existing_username_user = await self.user_repository.get_by_username(
            registration_data.username
        )

        if existing_username_user is not None:
            raise ConflictError(
                message="This username is already in use.",
                details={"field": "username"},
            )

        hashed_password = hash_password(registration_data.password)

        try:
            user = await self.user_repository.create(
                email=str(registration_data.email),
                hashed_password=hashed_password,
                username=registration_data.username,
                display_name=registration_data.display_name,
            )

            await self.session.commit()
            await self.session.refresh(user)

            return user

        except IntegrityError as exception:
            await self.session.rollback()

            raise ConflictError(
                message=(
                    "An account with the provided email or username already exists."
                ),
            ) from exception

        except Exception:
            await self.session.rollback()
            raise
