from unittest.mock import AsyncMock, Mock
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.profile import Profile
from app.repositories.profile_repository import ProfileRepository


async def test_get_by_user_id_returns_profile() -> None:
    session = AsyncMock(spec=AsyncSession)

    expected_profile = Profile(
        user_id=uuid4(),
        username="skill_user",
        display_name="Skill User",
    )

    result = Mock()
    result.scalar_one_or_none.return_value = expected_profile
    session.execute.return_value = result

    repository = ProfileRepository(session)

    returned_profile = await repository.get_by_user_id(expected_profile.user_id)

    assert returned_profile is expected_profile
    session.execute.assert_awaited_once()


async def test_get_by_username_returns_profile() -> None:
    session = AsyncMock(spec=AsyncSession)

    expected_profile = Profile(
        user_id=uuid4(),
        username="skill_user",
        display_name="Skill User",
    )

    result = Mock()
    result.scalar_one_or_none.return_value = expected_profile
    session.execute.return_value = result

    repository = ProfileRepository(session)

    returned_profile = await repository.get_by_username("SKILL_USER")

    assert returned_profile is expected_profile


async def test_update_changes_only_supplied_fields() -> None:
    session = AsyncMock(spec=AsyncSession)

    profile = Profile(
        user_id=uuid4(),
        username="skill_user",
        display_name="Skill User",
        bio="Old bio",
    )

    repository = ProfileRepository(session)

    updated_profile = await repository.update(
        profile,
        {
            "display_name": "Updated User",
            "bio": "Updated bio",
        },
    )

    assert updated_profile is profile
    assert profile.username == "skill_user"
    assert profile.display_name == "Updated User"
    assert profile.bio == "Updated bio"

    session.flush.assert_awaited_once()
