import pytest

from app.api.dependencies import (
    get_active_user,
    require_admin,
    require_moderator_or_admin,
)
from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.models.enums import UserRole, UserStatus
from tests.api.test_users import create_test_user


async def test_active_user_dependency_accepts_active_user() -> None:
    user = create_test_user(
        status=UserStatus.ACTIVE,
    )

    result = await get_active_user(user)

    assert result is user


async def test_active_user_dependency_rejects_suspended_user() -> None:
    user = create_test_user(
        status=UserStatus.SUSPENDED,
    )

    with pytest.raises(UnauthorizedError):
        await get_active_user(user)


async def test_admin_dependency_accepts_admin() -> None:
    user = create_test_user(
        role=UserRole.ADMIN,
    )

    result = await require_admin(user)

    assert result is user


async def test_admin_dependency_rejects_regular_user() -> None:
    user = create_test_user(
        role=UserRole.USER,
    )

    with pytest.raises(ForbiddenError):
        await require_admin(user)


@pytest.mark.parametrize(
    "role",
    [
        UserRole.MODERATOR,
        UserRole.ADMIN,
    ],
)
async def test_moderator_dependency_accepts_allowed_roles(
    role: UserRole,
) -> None:
    user = create_test_user(role=role)

    result = await require_moderator_or_admin(user)

    assert result is user


async def test_moderator_dependency_rejects_regular_user() -> None:
    user = create_test_user(
        role=UserRole.USER,
    )

    with pytest.raises(ForbiddenError):
        await require_moderator_or_admin(user)
