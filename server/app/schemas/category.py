from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CategoryBase(BaseModel):
    name: str = Field(
        min_length=3,
        max_length=100,
    )

    description: str | None = Field(
        default=None,
        max_length=1000,
    )

    icon: str | None = Field(
        default=None,
        max_length=100,
    )

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        normalized_name = " ".join(value.split())

        if not normalized_name:
            raise ValueError("Category name cannot be empty.")

        return normalized_name

    @field_validator("description", "icon")
    @classmethod
    def normalize_optional_text(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        normalized_value = value.strip()

        return normalized_value or None


class CategoryCreateRequest(CategoryBase):
    pass


class CategoryUpdateRequest(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=3,
        max_length=100,
    )

    description: str | None = Field(
        default=None,
        max_length=1000,
    )

    icon: str | None = Field(
        default=None,
        max_length=100,
    )

    is_active: bool | None = None

    @field_validator("name")
    @classmethod
    def normalize_optional_name(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        normalized_name = " ".join(value.split())

        if not normalized_name:
            raise ValueError("Category name cannot be empty.")

        return normalized_name

    @field_validator("description", "icon")
    @classmethod
    def normalize_optional_text(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        normalized_value = value.strip()

        return normalized_value or None


class CategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    slug: str
    description: str | None
    icon: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class CategoryListResponse(BaseModel):
    items: list[CategoryResponse]
    page: int
    page_size: int
    total: int
    pages: int
