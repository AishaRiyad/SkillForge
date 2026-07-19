from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.enums import ChallengeStatus


class ChallengeCreateRequest(BaseModel):
    title: str = Field(
        min_length=3,
        max_length=150,
    )

    description: str | None = None

    passing_score: int = Field(
        default=70,
        ge=0,
        le=100,
    )

    xp_reward: int = Field(
        default=100,
        ge=0,
        le=100_000,
    )

    max_attempts: int | None = Field(
        default=None,
        ge=1,
        le=100,
    )

    status: ChallengeStatus = ChallengeStatus.DRAFT

    @field_validator("title")
    @classmethod
    def normalize_title(cls, value: str) -> str:
        normalized = " ".join(value.split())

        if not normalized:
            raise ValueError("Challenge title cannot be empty.")

        return normalized

    @field_validator("description")
    @classmethod
    def normalize_description(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        normalized = value.strip()

        return normalized or None


class ChallengeUpdateRequest(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=3,
        max_length=150,
    )

    description: str | None = None

    passing_score: int | None = Field(
        default=None,
        ge=0,
        le=100,
    )

    xp_reward: int | None = Field(
        default=None,
        ge=0,
        le=100_000,
    )

    max_attempts: int | None = Field(
        default=None,
        ge=1,
        le=100,
    )

    status: ChallengeStatus | None = None
    is_active: bool | None = None


class ChallengeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    lesson_id: UUID
    title: str
    description: str | None
    passing_score: int
    xp_reward: int
    max_attempts: int | None
    status: ChallengeStatus
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ChallengeListResponse(BaseModel):
    items: list[ChallengeResponse]
    total: int
