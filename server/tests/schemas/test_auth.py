import pytest
from pydantic import ValidationError

from app.schemas.auth import LoginRequest


def test_login_request_normalizes_email() -> None:
    request = LoginRequest(
        email="  USER@Example.com  ",
        password="Password123",
    )

    assert str(request.email) == "user@example.com"


@pytest.mark.parametrize(
    "email",
    [
        "",
        "invalid-email",
        "user@",
    ],
)
def test_login_request_rejects_invalid_email(
    email: str,
) -> None:
    with pytest.raises(ValidationError):
        LoginRequest(
            email=email,
            password="Password123",
        )


def test_login_request_rejects_empty_password() -> None:
    with pytest.raises(ValidationError):
        LoginRequest(
            email="user@example.com",
            password="",
        )
