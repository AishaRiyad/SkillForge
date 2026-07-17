from datetime import timedelta
from uuid import uuid4

import pytest

from app.core.exceptions import UnauthorizedError
from app.core.tokens import (
    create_access_token,
    create_refresh_token,
    create_token,
    decode_token,
    get_token_user_id,
    hash_token,
)
from app.schemas.auth import TokenType


def test_access_token_contains_expected_claims() -> None:
    user_id = uuid4()

    token = create_access_token(user_id)

    payload = decode_token(
        token,
        expected_type=TokenType.ACCESS,
    )

    assert payload["sub"] == str(user_id)
    assert payload["type"] == TokenType.ACCESS.value
    assert payload["iss"] == "skillforge-api"
    assert payload["aud"] == "skillforge-client"
    assert "jti" in payload
    assert "iat" in payload
    assert "exp" in payload


def test_get_token_user_id_returns_subject() -> None:
    user_id = uuid4()
    token = create_access_token(user_id)

    decoded_user_id = get_token_user_id(
        token,
        expected_type=TokenType.ACCESS,
    )

    assert decoded_user_id == user_id


def test_refresh_token_cannot_be_used_as_access_token() -> None:
    token = create_refresh_token(uuid4())

    with pytest.raises(UnauthorizedError):
        decode_token(
            token,
            expected_type=TokenType.ACCESS,
        )


def test_expired_token_is_rejected() -> None:
    token = create_token(
        user_id=uuid4(),
        token_type=TokenType.ACCESS,
        expires_delta=timedelta(seconds=-1),
    )

    with pytest.raises(UnauthorizedError):
        decode_token(
            token,
            expected_type=TokenType.ACCESS,
        )


def test_modified_token_is_rejected() -> None:
    token = create_access_token(uuid4())

    header, payload, signature = token.split(".")

    middle_index = len(signature) // 2
    replacement = "a" if signature[middle_index] != "a" else "b"

    modified_signature = (
        signature[:middle_index] + replacement + signature[middle_index + 1 :]
    )

    modified_token = f"{header}.{payload}.{modified_signature}"

    with pytest.raises(UnauthorizedError):
        decode_token(
            modified_token,
            expected_type=TokenType.ACCESS,
        )


def test_hash_token_is_deterministic_and_hides_token() -> None:
    token = "example-refresh-token"

    first_hash = hash_token(token)
    second_hash = hash_token(token)

    assert first_hash == second_hash
    assert first_hash != token
    assert len(first_hash) == 64
