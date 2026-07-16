from datetime import UTC, datetime
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, UnauthorizedError
from app.core.security import hash_password
from app.models.enums import UserRole, UserStatus
from app.models.profile import Profile
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest
from app.schemas.user import UserRegistrationRequest
from app.services.auth_service import AuthService


def create_registration_data() -> UserRegistrationRequest:
    return UserRegistrationRequest(
        email="user@example.com",
        password="StrongPassword123",
        username="skill_user",
        display_name="Skill User",
    )


def create_login_user(
    *,
    password: str = "StrongPassword123",
    status: UserStatus = UserStatus.ACTIVE,
) -> User:
    user_id = uuid4()
    current_time = datetime.now(UTC)

    user = User(
        email="user@example.com",
        hashed_password=hash_password(password),
        role=UserRole.USER,
        status=status,
        is_email_verified=False,
    )

    user.id = user_id
    user.created_at = current_time
    user.updated_at = current_time

    user.profile = Profile(
        user_id=user_id,
        username="skill_user",
        display_name="Skill User",
        total_xp=0,
        current_level=1,
        current_streak=0,
        longest_streak=0,
    )

    user.profile.created_at = current_time
    user.profile.updated_at = current_time

    return user


async def test_register_user_creates_and_commits_user() -> None:
    session = AsyncMock(spec=AsyncSession)
    repository = AsyncMock(spec=UserRepository)

    created_user = User(
        email="user@example.com",
        hashed_password="hashed-password",
    )

    repository.get_by_email.return_value = None
    repository.get_by_username.return_value = None
    repository.create.return_value = created_user

    service = AuthService(
        session=session,
        user_repository=repository,
    )

    result = await service.register_user(create_registration_data())

    assert result is created_user

    repository.get_by_email.assert_awaited_once_with("user@example.com")
    repository.get_by_username.assert_awaited_once_with("skill_user")
    repository.create.assert_awaited_once()

    session.commit.assert_awaited_once()
    session.refresh.assert_awaited_once_with(created_user)
    session.rollback.assert_not_awaited()


async def test_register_user_rejects_duplicate_email() -> None:
    session = AsyncMock(spec=AsyncSession)
    repository = AsyncMock(spec=UserRepository)

    repository.get_by_email.return_value = Mock(spec=User)

    service = AuthService(
        session=session,
        user_repository=repository,
    )

    with pytest.raises(ConflictError) as exception_info:
        await service.register_user(create_registration_data())

    assert exception_info.value.status_code == 409
    assert exception_info.value.details == {"field": "email"}

    repository.get_by_username.assert_not_awaited()
    repository.create.assert_not_awaited()
    session.commit.assert_not_awaited()


async def test_register_user_rejects_duplicate_username() -> None:
    session = AsyncMock(spec=AsyncSession)
    repository = AsyncMock(spec=UserRepository)

    repository.get_by_email.return_value = None
    repository.get_by_username.return_value = Mock(spec=User)

    service = AuthService(
        session=session,
        user_repository=repository,
    )

    with pytest.raises(ConflictError) as exception_info:
        await service.register_user(create_registration_data())

    assert exception_info.value.status_code == 409
    assert exception_info.value.details == {"field": "username"}

    repository.create.assert_not_awaited()
    session.commit.assert_not_awaited()


async def test_login_returns_access_and_refresh_tokens() -> None:
    session = AsyncMock(spec=AsyncSession)
    repository = AsyncMock(spec=UserRepository)

    repository.get_by_email.return_value = create_login_user()

    service = AuthService(
        session=session,
        user_repository=repository,
    )

    response = await service.login_user(
        LoginRequest(
            email="user@example.com",
            password="StrongPassword123",
        )
    )

    assert response.tokens.token_type == "bearer"
    assert response.tokens.access_token
    assert response.tokens.refresh_token
    assert response.user.email == "user@example.com"


async def test_login_rejects_unknown_email() -> None:
    session = AsyncMock(spec=AsyncSession)
    repository = AsyncMock(spec=UserRepository)

    repository.get_by_email.return_value = None

    service = AuthService(
        session=session,
        user_repository=repository,
    )

    with pytest.raises(UnauthorizedError):
        await service.login_user(
            LoginRequest(
                email="missing@example.com",
                password="StrongPassword123",
            )
        )


async def test_login_rejects_wrong_password() -> None:
    session = AsyncMock(spec=AsyncSession)
    repository = AsyncMock(spec=UserRepository)

    repository.get_by_email.return_value = create_login_user()

    service = AuthService(
        session=session,
        user_repository=repository,
    )

    with pytest.raises(UnauthorizedError):
        await service.login_user(
            LoginRequest(
                email="user@example.com",
                password="WrongPassword123",
            )
        )


async def test_login_rejects_inactive_account() -> None:
    session = AsyncMock(spec=AsyncSession)
    repository = AsyncMock(spec=UserRepository)

    repository.get_by_email.return_value = create_login_user(
        status=UserStatus.SUSPENDED
    )

    service = AuthService(
        session=session,
        user_repository=repository,
    )

    with pytest.raises(UnauthorizedError):
        await service.login_user(
            LoginRequest(
                email="user@example.com",
                password="StrongPassword123",
            )
        )
