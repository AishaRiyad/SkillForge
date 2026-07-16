import re
from datetime import datetime
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
)

from app.models.enums import UserRole, UserStatus

USERNAME_PATTERN = re.compile(r"^[a-z0-9_]+$")


class UserRegistrationRequest(BaseModel):
    email: EmailStr
    password: str = Field(
        min_length=8,
        max_length=128,
        repr=False,
    )
    username: str = Field(
        min_length=3,
        max_length=30,
    )
    display_name: str = Field(
        min_length=2,
        max_length=100,
    )

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return str(value).strip().lower()

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        normalized_username = value.strip().lower()

        if not USERNAME_PATTERN.fullmatch(normalized_username):
            raise ValueError(
                "Username may contain only lowercase letters, numbers, and underscores."
            )

        return normalized_username

    @field_validator("display_name")
    @classmethod
    def normalize_display_name(cls, value: str) -> str:
        normalized_name = " ".join(value.split())

        if not normalized_name:
            raise ValueError("Display name cannot be empty.")

        return normalized_name

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, value: str) -> str:
        if not any(character.islower() for character in value):
            raise ValueError("Password must contain at least one lowercase letter.")

        if not any(character.isupper() for character in value):
            raise ValueError("Password must contain at least one uppercase letter.")

        if not any(character.isdigit() for character in value):
            raise ValueError("Password must contain at least one number.")

        return value


class ProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: UUID
    username: str
    display_name: str
    bio: str | None
    avatar_url: str | None
    total_xp: int
    current_level: int
    current_streak: int
    longest_streak: int
    created_at: datetime
    updated_at: datetime


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: EmailStr
    role: UserRole
    status: UserStatus
    is_email_verified: bool
    created_at: datetime
    updated_at: datetime
    profile: ProfileResponse
