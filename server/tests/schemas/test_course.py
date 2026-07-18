from decimal import Decimal
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.models.enums import CourseStatus
from app.schemas.course import (
    CourseCreateRequest,
    CourseUpdateRequest,
)


def test_course_create_normalizes_fields() -> None:
    request = CourseCreateRequest(
        category_id=uuid4(),
        title="  FastAPI   Fundamentals  ",
        short_description="  Learn FastAPI  ",
        description="  Detailed course  ",
        thumbnail_url="  https://example.com/course.png  ",
        price=Decimal("12.50"),
    )

    assert request.title == "FastAPI Fundamentals"
    assert request.short_description == "Learn FastAPI"
    assert request.description == "Detailed course"
    assert request.thumbnail_url == ("https://example.com/course.png")
    assert request.status == CourseStatus.DRAFT


def test_course_update_is_partial() -> None:
    request = CourseUpdateRequest(
        xp_reward=500,
    )

    assert request.model_dump(exclude_unset=True) == {"xp_reward": 500}


@pytest.mark.parametrize(
    "difficulty_level",
    [0, 6],
)
def test_course_rejects_invalid_difficulty(
    difficulty_level: int,
) -> None:
    with pytest.raises(ValidationError):
        CourseCreateRequest(
            category_id=uuid4(),
            title="FastAPI Course",
            difficulty_level=difficulty_level,
        )


def test_course_rejects_negative_price() -> None:
    with pytest.raises(ValidationError):
        CourseCreateRequest(
            category_id=uuid4(),
            title="FastAPI Course",
            price=Decimal("-1.00"),
        )
