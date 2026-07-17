from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from hashlib import sha256
from typing import Any
from uuid import UUID, uuid4

import jwt
from jwt import InvalidTokenError

from app.core.config import settings
from app.core.exceptions import UnauthorizedError
from app.schemas.auth import TokenType


@dataclass(frozen=True, slots=True)
class TokenMetadata:
    user_id: UUID
    jti: UUID
    expires_at: datetime


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
        expires_delta=timedelta(
            minutes=settings.access_token_expire_minutes,
        ),
    )


def create_refresh_token(user_id: UUID) -> str:
    return create_token(
        user_id=user_id,
        token_type=TokenType.REFRESH,
        expires_delta=timedelta(
            days=settings.refresh_token_expire_days,
        ),
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


def hash_token(token: str) -> str:
    """Create a deterministic SHA-256 hash for token storage."""

    return sha256(token.encode("utf-8")).hexdigest()


def get_token_metadata(
    token: str,
    *,
    expected_type: TokenType,
) -> TokenMetadata:
    payload = decode_token(
        token,
        expected_type=expected_type,
    )

    try:
        user_id = UUID(str(payload["sub"]))
        jti = UUID(str(payload["jti"]))
        expires_at = datetime.fromtimestamp(
            int(payload["exp"]),
            tz=UTC,
        )
    except (KeyError, TypeError, ValueError) as exception:
        raise UnauthorizedError(
            message="The authentication token metadata is invalid."
        ) from exception

    return TokenMetadata(
        user_id=user_id,
        jti=jti,
        expires_at=expires_at,
    )
