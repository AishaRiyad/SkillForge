from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)

from app.models.enums import CourseStatus


class CourseCreateRequest(BaseModel):
    category_id: UUID

    title: str = Field(
        min_length=3,
        max_length=150,
    )

    short_description: str | None = Field(
        default=None,
        max_length=300,
    )

    description: str | None = None

    thumbnail_url: str | None = Field(
        default=None,
        max_length=2048,
    )

    estimated_minutes: int = Field(
        default=0,
        ge=0,
        le=100_000,
    )

    difficulty_level: int = Field(
        default=1,
        ge=1,
        le=5,
    )

    xp_reward: int = Field(
        default=0,
        ge=0,
        le=1_000_000,
    )

    price: Decimal = Field(
        default=Decimal("0.00"),
        ge=Decimal("0.00"),
        max_digits=10,
        decimal_places=2,
    )

    status: CourseStatus = CourseStatus.DRAFT

    @field_validator("title")
    @classmethod
    def normalize_title(cls, value: str) -> str:
        normalized_title = " ".join(value.split())

        if not normalized_title:
            raise ValueError("Course title cannot be empty.")

        return normalized_title

    @field_validator(
        "short_description",
        "description",
        "thumbnail_url",
    )
    @classmethod
    def normalize_optional_text(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        normalized_value = value.strip()

        return normalized_value or None


class CourseUpdateRequest(BaseModel):
    category_id: UUID | None = None

    title: str | None = Field(
        default=None,
        min_length=3,
        max_length=150,
    )

    short_description: str | None = Field(
        default=None,
        max_length=300,
    )

    description: str | None = None

    thumbnail_url: str | None = Field(
        default=None,
        max_length=2048,
    )

    estimated_minutes: int | None = Field(
        default=None,
        ge=0,
        le=100_000,
    )

    difficulty_level: int | None = Field(
        default=None,
        ge=1,
        le=5,
    )

    xp_reward: int | None = Field(
        default=None,
        ge=0,
        le=1_000_000,
    )

    price: Decimal | None = Field(
        default=None,
        ge=Decimal("0.00"),
        max_digits=10,
        decimal_places=2,
    )

    status: CourseStatus | None = None
    is_active: bool | None = None

    @field_validator("title")
    @classmethod
    def normalize_optional_title(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        normalized_title = " ".join(value.split())

        if not normalized_title:
            raise ValueError("Course title cannot be empty.")

        return normalized_title

    @field_validator(
        "short_description",
        "description",
        "thumbnail_url",
    )
    @classmethod
    def normalize_optional_text(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        normalized_value = value.strip()

        return normalized_value or None


class CourseCategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    slug: str


class CourseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    category_id: UUID
    title: str
    slug: str
    short_description: str | None
    description: str | None
    thumbnail_url: str | None
    estimated_minutes: int
    difficulty_level: int
    xp_reward: int
    price: Decimal
    status: CourseStatus
    is_active: bool
    category: CourseCategoryResponse
    created_at: datetime
    updated_at: datetime


class CourseListResponse(BaseModel):
    items: list[CourseResponse]
    page: int
    page_size: int
    total: int
    pages: int
