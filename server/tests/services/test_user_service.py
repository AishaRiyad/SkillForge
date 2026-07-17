from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError
from app.models.profile import Profile
from app.models.user import User
from app.repositories.profile_repository import ProfileRepository
from app.schemas.user import ProfileUpdateRequest
from app.services.user_service import UserService


def create_user_with_profile() -> tuple[User, Profile]:
    user_id = uuid4()

    user = User(
        email="user@example.com",
        hashed_password="hidden-hash",
    )
    user.id = user_id

    profile = Profile(
        user_id=user_id,
        username="skill_user",
        display_name="Skill User",
        bio=None,
        avatar_url=None,
    )

    user.profile = profile

    return user, profile


async def test_update_profile_commits_changes() -> None:
    session = AsyncMock(spec=AsyncSession)
    repository = AsyncMock(spec=ProfileRepository)

    user, profile = create_user_with_profile()

    repository.get_by_user_id.return_value = profile
    repository.get_by_username.return_value = None
    repository.update.return_value = profile

    service = UserService(
        session=session,
        profile_repository=repository,
    )

    result = await service.update_profile(
        user,
        ProfileUpdateRequest(
            username="new_username",
            display_name="New Name",
        ),
    )

    assert result is profile

    repository.update.assert_awaited_once_with(
        profile,
        {
            "username": "new_username",
            "display_name": "New Name",
        },
    )

    session.commit.assert_awaited_once()
    session.refresh.assert_awaited_once_with(profile)
    session.rollback.assert_not_awaited()


async def test_update_profile_rejects_duplicate_username() -> None:
    session = AsyncMock(spec=AsyncSession)
    repository = AsyncMock(spec=ProfileRepository)

    user, profile = create_user_with_profile()

    duplicate_profile = Profile(
        user_id=uuid4(),
        username="existing_user",
        display_name="Existing User",
    )

    repository.get_by_user_id.return_value = profile
    repository.get_by_username.return_value = duplicate_profile

    service = UserService(
        session=session,
        profile_repository=repository,
    )

    with pytest.raises(ConflictError) as exception_info:
        await service.update_profile(
            user,
            ProfileUpdateRequest(username="existing_user"),
        )

    assert exception_info.value.details == {"field": "username"}

    repository.update.assert_not_awaited()
    session.commit.assert_not_awaited()


async def test_update_profile_with_empty_payload_does_not_commit() -> None:
    session = AsyncMock(spec=AsyncSession)
    repository = AsyncMock(spec=ProfileRepository)

    user, profile = create_user_with_profile()

    repository.get_by_user_id.return_value = profile

    service = UserService(
        session=session,
        profile_repository=repository,
    )

    result = await service.update_profile(
        user,
        ProfileUpdateRequest(),
    )

    assert result is profile

    repository.update.assert_not_awaited()
    session.commit.assert_not_awaited()
