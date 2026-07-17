import pytest
from pydantic import ValidationError

from app.schemas.user import ProfileUpdateRequest


def test_profile_update_normalizes_fields() -> None:
    request = ProfileUpdateRequest(
        username="  AISHA_DEV  ",
        display_name="  Aisha   Developer  ",
        bio="  Python learner  ",
        avatar_url="  https://example.com/avatar.png  ",
    )

    assert request.username == "aisha_dev"
    assert request.display_name == "Aisha Developer"
    assert request.bio == "Python learner"
    assert request.avatar_url == ("https://example.com/avatar.png")


def test_profile_update_supports_partial_data() -> None:
    request = ProfileUpdateRequest(display_name="Aisha Developer")

    assert request.model_dump(exclude_unset=True) == {"display_name": "Aisha Developer"}


def test_profile_update_can_clear_optional_fields() -> None:
    request = ProfileUpdateRequest(
        bio=None,
        avatar_url=None,
    )

    assert request.model_dump(exclude_unset=True) == {
        "bio": None,
        "avatar_url": None,
    }


@pytest.mark.parametrize(
    "username",
    [
        "ab",
        "user name",
        "user-name",
        "user@name",
    ],
)
def test_profile_update_rejects_invalid_username(
    username: str,
) -> None:
    with pytest.raises(ValidationError):
        ProfileUpdateRequest(username=username)


def test_profile_update_rejects_long_bio() -> None:
    with pytest.raises(ValidationError):
        ProfileUpdateRequest(bio="a" * 501)
