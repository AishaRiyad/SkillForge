from unittest.mock import AsyncMock, Mock
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.user_repository import UserRepository


async def test_get_by_email_returns_matching_user() -> None:
    session = AsyncMock(spec=AsyncSession)

    expected_user = User(
        email="user@example.com",
        hashed_password="hashed-password",
    )

    result = Mock()
    result.scalar_one_or_none.return_value = expected_user
    session.execute.return_value = result

    repository = UserRepository(session)

    returned_user = await repository.get_by_email("USER@Example.com")

    assert returned_user is expected_user
    session.execute.assert_awaited_once()


async def test_get_by_email_returns_none_when_missing() -> None:
    session = AsyncMock(spec=AsyncSession)

    result = Mock()
    result.scalar_one_or_none.return_value = None
    session.execute.return_value = result

    repository = UserRepository(session)

    returned_user = await repository.get_by_email("missing@example.com")

    assert returned_user is None


async def test_get_by_id_returns_matching_user() -> None:
    session = AsyncMock(spec=AsyncSession)

    user_id = uuid4()
    expected_user = User(
        email="user@example.com",
        hashed_password="hashed-password",
    )

    result = Mock()
    result.scalar_one_or_none.return_value = expected_user
    session.execute.return_value = result

    repository = UserRepository(session)

    returned_user = await repository.get_by_id(user_id)

    assert returned_user is expected_user


async def test_create_adds_user_and_profile() -> None:
    session = AsyncMock(spec=AsyncSession)
    repository = UserRepository(session)

    created_user = await repository.create(
        email="USER@Example.com",
        hashed_password="hashed-password",
        username="SKILL_USER",
        display_name="Aisha Ahmad",
    )

    assert created_user.email == "user@example.com"
    assert created_user.hashed_password == "hashed-password"

    assert created_user.profile.username == "skill_user"
    assert created_user.profile.display_name == "Aisha Ahmad"

    session.add.assert_called_once_with(created_user)
    session.flush.assert_awaited_once()
