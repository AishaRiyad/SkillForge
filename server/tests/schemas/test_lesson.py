
import pytest
from pydantic import ValidationError

from app.models.enums import LessonStatus
from app.schemas.lesson import (
    LessonCreateRequest,
    LessonUpdateRequest,
)


def test_lesson_create_normalizes_fields() -> None:
    request = LessonCreateRequest(
        title="  Introduction   to FastAPI  ",
        content="  Lesson content  ",
        video_url="  https://example.com/video  ",
        position=1,
    )

    assert request.title == "Introduction to FastAPI"
    assert request.content == "Lesson content"
    assert request.video_url == "https://example.com/video"
    assert request.status == LessonStatus.DRAFT


def test_lesson_update_is_partial() -> None:
    request = LessonUpdateRequest(
        estimated_minutes=15,
    )

    assert request.model_dump(exclude_unset=True) == {"estimated_minutes": 15}


def test_lesson_rejects_invalid_position() -> None:
    with pytest.raises(ValidationError):
        LessonCreateRequest(
            title="FastAPI Lesson",
            position=0,
        )
