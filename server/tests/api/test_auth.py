from datetime import UTC, datetime
from uuid import uuid4

from fastapi import FastAPI
from httpx import AsyncClient

from app.api.dependencies import get_auth_service
from app.models.enums import UserRole, UserStatus
from app.models.profile import Profile
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    TokenPair,
)
from app.schemas.user import (
    UserRegistrationRequest,
    UserResponse,
)


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

    async def login_user(
        self,
        login_data: LoginRequest,
    ) -> LoginResponse:
        registration = UserRegistrationRequest(
            email=login_data.email,
            password="StrongPassword123",
            username="skill_user",
            display_name="Skill User",
        )

        user = await self.register_user(registration)

        return LoginResponse(
            user=UserResponse.model_validate(user),
            tokens=TokenPair(
                access_token="test-access-token",
                refresh_token="test-refresh-token",
                access_token_expires_in=1800,
            ),
        )

    async def refresh_tokens(
        self,
        raw_refresh_token: str,
    ) -> TokenPair:
        return TokenPair(
            access_token="rotated-access-token",
            refresh_token="rotated-refresh-token",
            access_token_expires_in=1800,
        )

    async def logout(
        self,
        raw_refresh_token: str,
    ) -> None:
        return None


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


async def test_login_returns_token_pair(
    client: AsyncClient,
    application: FastAPI,
) -> None:
    application.dependency_overrides[get_auth_service] = lambda: FakeAuthService()

    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "USER@example.com",
            "password": "StrongPassword123",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["user"]["email"] == "user@example.com"
    assert data["tokens"] == {
        "access_token": "test-access-token",
        "refresh_token": "test-refresh-token",
        "token_type": "bearer",
        "access_token_expires_in": 1800,
    }

    application.dependency_overrides.clear()


async def test_login_rejects_invalid_request(
    client: AsyncClient,
) -> None:
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "invalid-email",
            "password": "",
        },
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


async def test_refresh_returns_rotated_token_pair(
    client: AsyncClient,
    application: FastAPI,
) -> None:
    application.dependency_overrides[get_auth_service] = lambda: FakeAuthService()

    response = await client.post(
        "/api/v1/auth/refresh",
        json={
            "refresh_token": "existing-refresh-token",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "access_token": "rotated-access-token",
        "refresh_token": "rotated-refresh-token",
        "token_type": "bearer",
        "access_token_expires_in": 1800,
    }

    application.dependency_overrides.clear()


async def test_logout_returns_no_content(
    client: AsyncClient,
    application: FastAPI,
) -> None:
    application.dependency_overrides[get_auth_service] = lambda: FakeAuthService()

    response = await client.post(
        "/api/v1/auth/logout",
        json={
            "refresh_token": "existing-refresh-token",
        },
    )

    assert response.status_code == 204
    assert response.content == b""

    application.dependency_overrides.clear()
