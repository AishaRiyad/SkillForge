from unittest.mock import AsyncMock, Mock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserRegistrationRequest
from app.services.auth_service import AuthService


def create_registration_data() -> UserRegistrationRequest:
    return UserRegistrationRequest(
        email="user@example.com",
        password="StrongPassword123",
        username="skill_user",
        display_name="Skill User",
    )


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
