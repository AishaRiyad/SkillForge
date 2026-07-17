from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import ConflictError, UnauthorizedError
from app.core.security import hash_password, verify_password
from app.core.tokens import (
    create_access_token,
    create_refresh_token,
    get_token_metadata,
    hash_token,
)
from app.models.enums import UserStatus
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.repositories.refresh_token_repository import (
    RefreshTokenRepository,
)
from app.repositories.user_repository import UserRepository
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    TokenPair,
    TokenType,
)
from app.schemas.user import (
    UserRegistrationRequest,
    UserResponse,
)


class AuthService:
    def __init__(
        self,
        session: AsyncSession,
        user_repository: UserRepository,
        refresh_token_repository: RefreshTokenRepository,
    ) -> None:
        self.session = session
        self.user_repository = user_repository
        self.refresh_token_repository = refresh_token_repository

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

        self._ensure_user_is_active(user)

        try:
            tokens = await self._create_token_pair(user)

            await self.session.commit()

            return LoginResponse(
                user=UserResponse.model_validate(user),
                tokens=tokens,
            )
        except Exception:
            await self.session.rollback()
            raise

    async def refresh_tokens(
        self,
        raw_refresh_token: str,
    ) -> TokenPair:
        metadata = get_token_metadata(
            raw_refresh_token,
            expected_type=TokenType.REFRESH,
        )

        stored_token = await self.refresh_token_repository.get_active_by_token_hash(
            hash_token(raw_refresh_token),
            lock_for_update=True,
        )

        self._validate_stored_refresh_token(
            stored_token=stored_token,
            expected_user_id=metadata.user_id,
            expected_jti=metadata.jti,
        )

        user = await self.user_repository.get_by_id(metadata.user_id)

        if user is None:
            raise UnauthorizedError(message="The token user no longer exists.")

        self._ensure_user_is_active(user)

        try:
            new_tokens = await self._create_token_pair(user)

            new_metadata = get_token_metadata(
                new_tokens.refresh_token,
                expected_type=TokenType.REFRESH,
            )

            assert stored_token is not None

            await self.refresh_token_repository.revoke(
                stored_token,
                replaced_by_jti=new_metadata.jti,
            )

            await self.session.commit()

            return new_tokens

        except Exception:
            await self.session.rollback()
            raise

    async def logout(
        self,
        raw_refresh_token: str,
    ) -> None:
        metadata = get_token_metadata(
            raw_refresh_token,
            expected_type=TokenType.REFRESH,
        )

        stored_token = await self.refresh_token_repository.get_active_by_token_hash(
            hash_token(raw_refresh_token),
            lock_for_update=True,
        )

        if stored_token is None:
            return

        self._validate_stored_refresh_token(
            stored_token=stored_token,
            expected_user_id=metadata.user_id,
            expected_jti=metadata.jti,
        )

        try:
            await self.refresh_token_repository.revoke(
                stored_token,
            )

            await self.session.commit()

        except Exception:
            await self.session.rollback()
            raise

    async def _create_token_pair(
        self,
        user: User,
    ) -> TokenPair:
        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)

        refresh_metadata = get_token_metadata(
            refresh_token,
            expected_type=TokenType.REFRESH,
        )

        await self.refresh_token_repository.create(
            user_id=user.id,
            jti=refresh_metadata.jti,
            token_hash=hash_token(refresh_token),
            expires_at=refresh_metadata.expires_at,
        )

        return TokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
            access_token_expires_in=(settings.access_token_expire_minutes * 60),
        )

    @staticmethod
    def _ensure_user_is_active(
        user: User,
    ) -> None:
        if user.status != UserStatus.ACTIVE:
            raise UnauthorizedError(message="This account is not active.")

    @staticmethod
    def _validate_stored_refresh_token(
        *,
        stored_token: RefreshToken | None,
        expected_user_id: UUID,
        expected_jti: UUID,
    ) -> None:
        if stored_token is None:
            raise UnauthorizedError(
                message="The refresh token is invalid or has been revoked."
            )

        if stored_token.user_id != expected_user_id or stored_token.jti != expected_jti:
            raise UnauthorizedError(message="The refresh token session is invalid.")
