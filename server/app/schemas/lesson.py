from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.enums import LessonStatus


class LessonCreateRequest(BaseModel):
    title: str = Field(
        min_length=3,
        max_length=150,
    )

    content: str | None = None

    video_url: str | None = Field(
        default=None,
        max_length=2048,
    )

    estimated_minutes: int = Field(
        default=0,
        ge=0,
        le=10_000,
    )

    position: int = Field(
        ge=1,
    )

    is_preview: bool = False
    status: LessonStatus = LessonStatus.DRAFT

    @field_validator("title")
    @classmethod
    def normalize_title(cls, value: str) -> str:
        normalized = " ".join(value.split())

        if not normalized:
            raise ValueError("Lesson title cannot be empty.")

        return normalized

    @field_validator("content", "video_url")
    @classmethod
    def normalize_optional_text(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        normalized = value.strip()

        return normalized or None


class LessonUpdateRequest(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=3,
        max_length=150,
    )

    content: str | None = None

    video_url: str | None = Field(
        default=None,
        max_length=2048,
    )

    estimated_minutes: int | None = Field(
        default=None,
        ge=0,
        le=10_000,
    )

    position: int | None = Field(
        default=None,
        ge=1,
    )

    is_preview: bool | None = None
    status: LessonStatus | None = None
    is_active: bool | None = None

    @field_validator("title")
    @classmethod
    def normalize_optional_title(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        normalized = " ".join(value.split())

        if not normalized:
            raise ValueError("Lesson title cannot be empty.")

        return normalized

    @field_validator("content", "video_url")
    @classmethod
    def normalize_optional_text(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        normalized = value.strip()

        return normalized or None


class LessonResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    course_id: UUID
    title: str
    slug: str
    content: str | None
    video_url: str | None
    estimated_minutes: int
    position: int
    is_preview: bool
    status: LessonStatus
    is_active: bool
    created_at: datetime
    updated_at: datetime


class LessonListResponse(BaseModel):
    items: list[LessonResponse]
    total: int
