import pytest
from pydantic import ValidationError

from app.schemas.category import (
    CategoryCreateRequest,
    CategoryUpdateRequest,
)
from app.utils.slug import generate_slug


def test_category_create_normalizes_fields() -> None:
    request = CategoryCreateRequest(
        name="  Machine   Learning  ",
        description="  Learn ML fundamentals  ",
        icon="  brain  ",
    )

    assert request.name == "Machine Learning"
    assert request.description == "Learn ML fundamentals"
    assert request.icon == "brain"


def test_category_update_supports_partial_data() -> None:
    request = CategoryUpdateRequest(description="Updated description")

    assert request.model_dump(exclude_unset=True) == {
        "description": "Updated description"
    }


def test_category_update_can_clear_optional_fields() -> None:
    request = CategoryUpdateRequest(
        description=None,
        icon=None,
    )

    assert request.model_dump(exclude_unset=True) == {
        "description": None,
        "icon": None,
    }


def test_category_rejects_short_name() -> None:
    with pytest.raises(ValidationError):
        CategoryCreateRequest(name="AI")


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("Machine Learning", "machine-learning"),
        ("Web Development", "web-development"),
        ("  Backend   Engineering  ", "backend-engineering"),
    ],
)
def test_generate_slug(
    value: str,
    expected: str,
) -> None:
    assert generate_slug(value) == expected
