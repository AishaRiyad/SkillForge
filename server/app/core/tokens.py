from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID, uuid4

import jwt
from jwt import InvalidTokenError

from app.core.config import settings
from app.core.exceptions import UnauthorizedError
from app.schemas.auth import TokenType


def create_token(
    *,
    user_id: UUID,
    token_type: TokenType,
    expires_delta: timedelta,
) -> str:
    issued_at = datetime.now(UTC)
    expires_at = issued_at + expires_delta

    payload: dict[str, Any] = {
        "sub": str(user_id),
        "type": token_type.value,
        "jti": str(uuid4()),
        "iat": issued_at,
        "exp": expires_at,
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience,
    }

    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def create_access_token(user_id: UUID) -> str:
    return create_token(
        user_id=user_id,
        token_type=TokenType.ACCESS,
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )


def create_refresh_token(user_id: UUID) -> str:
    return create_token(
        user_id=user_id,
        token_type=TokenType.REFRESH,
        expires_delta=timedelta(days=settings.refresh_token_expire_days),
    )


def decode_token(
    token: str,
    *,
    expected_type: TokenType,
) -> dict[str, Any]:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
            audience=settings.jwt_audience,
            issuer=settings.jwt_issuer,
            options={
                "require": [
                    "sub",
                    "type",
                    "jti",
                    "iat",
                    "exp",
                    "iss",
                    "aud",
                ],
            },
        )
    except InvalidTokenError as exception:
        raise UnauthorizedError(
            message="The authentication token is invalid or expired."
        ) from exception

    if payload.get("type") != expected_type.value:
        raise UnauthorizedError(
            message="The provided token type is not valid for this action."
        )

    try:
        UUID(str(payload["sub"]))
    except (ValueError, TypeError) as exception:
        raise UnauthorizedError(
            message="The authentication token subject is invalid."
        ) from exception

    return payload


def get_token_user_id(
    token: str,
    *,
    expected_type: TokenType,
) -> UUID:
    payload = decode_token(
        token,
        expected_type=expected_type,
    )

    return UUID(str(payload["sub"]))
