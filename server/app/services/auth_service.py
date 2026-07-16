from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import ConflictError, UnauthorizedError
from app.core.security import hash_password, verify_password
from app.core.tokens import create_access_token, create_refresh_token
from app.models.enums import UserStatus
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, LoginResponse, TokenPair
from app.schemas.user import UserRegistrationRequest, UserResponse


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

    async def login_user(
        self,
        login_data: LoginRequest,
    ) -> LoginResponse:
        user = await self.user_repository.get_by_email(str(login_data.email))

        if user is None or not verify_password(
            login_data.password,
            user.hashed_password,
        ):
            raise UnauthorizedError(message="The email or password is incorrect.")

        if user.status != UserStatus.ACTIVE:
            raise UnauthorizedError(message="This account is not active.")

        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)

        return LoginResponse(
            user=UserResponse.model_validate(user),
            tokens=TokenPair(
                access_token=access_token,
                refresh_token=refresh_token,
                access_token_expires_in=(settings.access_token_expire_minutes * 60),
            ),
        )
