from datetime import UTC, datetime
from uuid import uuid4

from fastapi import FastAPI
from httpx import AsyncClient

from app.api.dependencies import get_auth_service
from app.models.enums import UserRole, UserStatus
from app.models.profile import Profile
from app.models.user import User
from app.schemas.user import UserRegistrationRequest


class FakeAuthService:
    async def register_user(
        self,
        registration_data: UserRegistrationRequest,
    ) -> User:
        current_time = datetime.now(UTC)
        user_id = uuid4()

        user = User(
            email=str(registration_data.email),
            hashed_password="hidden-hash",
            role=UserRole.USER,
            status=UserStatus.ACTIVE,
            is_email_verified=False,
        )

        user.id = user_id
        user.created_at = current_time
        user.updated_at = current_time

        user.profile = Profile(
            user_id=user_id,
            username=registration_data.username,
            display_name=registration_data.display_name,
            total_xp=0,
            current_level=1,
            current_streak=0,
            longest_streak=0,
        )

        user.profile.created_at = current_time
        user.profile.updated_at = current_time

        return user


async def test_register_user_returns_created_user(
    client: AsyncClient,
    application: FastAPI,
) -> None:
    application.dependency_overrides[get_auth_service] = lambda: FakeAuthService()

    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "USER@example.com",
            "password": "StrongPassword123",
            "username": "skill_user",
            "display_name": "Skill User",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["email"] == "user@example.com"
    assert data["role"] == "user"
    assert data["status"] == "active"
    assert data["is_email_verified"] is False

    assert data["profile"]["username"] == "skill_user"
    assert data["profile"]["display_name"] == "Skill User"
    assert data["profile"]["total_xp"] == 0
    assert data["profile"]["current_level"] == 1

    assert "password" not in data
    assert "hashed_password" not in data

    application.dependency_overrides.clear()


async def test_register_user_rejects_invalid_data(
    client: AsyncClient,
) -> None:
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "invalid-email",
            "password": "weak",
            "username": "x",
            "display_name": "",
        },
    )

    assert response.status_code == 422

    data = response.json()

    assert data["error"]["code"] == "VALIDATION_ERROR"
    assert data["request_id"] == response.headers["X-Request-ID"]
