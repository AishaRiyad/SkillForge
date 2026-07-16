import pytest
from pydantic import ValidationError

from app.schemas.user import UserRegistrationRequest


def test_registration_schema_normalizes_input() -> None:
    registration = UserRegistrationRequest(
        email="  USER@Example.com  ",
        password="StrongPassword123",
        username="  Skill_User  ",
        display_name="  Aisha   Ahmad  ",
    )

    assert str(registration.email) == "user@example.com"
    assert registration.username == "skill_user"
    assert registration.display_name == "Aisha Ahmad"


@pytest.mark.parametrize(
    "username",
    [
        "ab",
        "user name",
        "user-name",
        "user@name",
        "اسم",
    ],
)
def test_registration_rejects_invalid_username(
    username: str,
) -> None:
    with pytest.raises(ValidationError):
        UserRegistrationRequest(
            email="user@example.com",
            password="StrongPassword123",
            username=username,
            display_name="Aisha Ahmad",
        )


@pytest.mark.parametrize(
    "password",
    [
        "short1A",
        "onlylowercase1",
        "ONLYUPPERCASE1",
        "NoNumbersHere",
    ],
)
def test_registration_rejects_weak_password(
    password: str,
) -> None:
    with pytest.raises(ValidationError):
        UserRegistrationRequest(
            email="user@example.com",
            password=password,
            username="skill_user",
            display_name="Aisha Ahmad",
        )


def test_registration_rejects_invalid_email() -> None:
    with pytest.raises(ValidationError):
        UserRegistrationRequest(
            email="not-an-email",
            password="StrongPassword123",
            username="skill_user",
            display_name="Aisha Ahmad",
        )
