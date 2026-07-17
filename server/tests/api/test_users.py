from datetime import UTC, datetime
from uuid import uuid4

from fastapi import FastAPI
from httpx import AsyncClient

from app.api.dependencies import (
    get_current_user,
    get_user_service,
)
from app.models.enums import UserRole, UserStatus
from app.models.profile import Profile
from app.models.user import User
from app.schemas.user import ProfileUpdateRequest


class FakeUserService:
    async def update_profile(
        self,
        user: User,
        update_request: ProfileUpdateRequest,
    ) -> Profile:
        update_data = update_request.model_dump(exclude_unset=True)

        for field_name, value in update_data.items():
            setattr(user.profile, field_name, value)

        return user.profile


def create_test_user(
    *,
    role: UserRole = UserRole.USER,
    status: UserStatus = UserStatus.ACTIVE,
) -> User:
    current_time = datetime.now(UTC)
    user_id = uuid4()

    user = User(
        email="user@example.com",
        hashed_password="hidden-hash",
        role=role,
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


async def test_get_me_returns_authenticated_user(
    client: AsyncClient,
    application: FastAPI,
) -> None:
    test_user = create_test_user()

    application.dependency_overrides[get_current_user] = lambda: test_user

    response = await client.get(
        "/api/v1/users/me",
        headers={
            "Authorization": "Bearer test-access-token",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == str(test_user.id)
    assert data["email"] == "user@example.com"
    assert data["role"] == "user"
    assert data["status"] == "active"
    assert data["profile"]["username"] == "skill_user"

    assert "hashed_password" not in data


async def test_get_me_rejects_missing_access_token(
    client: AsyncClient,
) -> None:
    response = await client.get("/api/v1/users/me")

    assert response.status_code == 401

    data = response.json()

    assert data["error"]["code"] == "UNAUTHORIZED"
    assert data["request_id"] == response.headers["X-Request-ID"]


async def test_update_profile_returns_updated_profile(
    client: AsyncClient,
    application: FastAPI,
) -> None:
    test_user = create_test_user()

    application.dependency_overrides[get_current_user] = lambda: test_user
    application.dependency_overrides[get_user_service] = lambda: FakeUserService()

    response = await client.patch(
        "/api/v1/users/me/profile",
        headers={
            "Authorization": "Bearer test-access-token",
        },
        json={
            "username": "updated_user",
            "display_name": "Updated User",
            "bio": "Learning FastAPI",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["username"] == "updated_user"
    assert data["display_name"] == "Updated User"
    assert data["bio"] == "Learning FastAPI"
    assert data["total_xp"] == 0


async def test_update_profile_rejects_invalid_username(
    client: AsyncClient,
    application: FastAPI,
) -> None:
    test_user = create_test_user()

    application.dependency_overrides[get_current_user] = lambda: test_user

    response = await client.patch(
        "/api/v1/users/me/profile",
        headers={
            "Authorization": "Bearer test-access-token",
        },
        json={
            "username": "invalid username",
        },
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == ("VALIDATION_ERROR")


async def test_update_profile_requires_authentication(
    client: AsyncClient,
) -> None:
    response = await client.patch(
        "/api/v1/users/me/profile",
        json={
            "display_name": "Updated User",
        },
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"
