from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.refresh_token import RefreshToken
from app.repositories.refresh_token_repository import (
    RefreshTokenRepository,
)


async def test_create_adds_refresh_token() -> None:
    session = AsyncMock(spec=AsyncSession)
    repository = RefreshTokenRepository(session)

    user_id = uuid4()
    jti = uuid4()
    expires_at = datetime.now(UTC) + timedelta(days=7)

    token = await repository.create(
        user_id=user_id,
        jti=jti,
        token_hash="a" * 64,
        expires_at=expires_at,
    )

    assert token.user_id == user_id
    assert token.jti == jti
    assert token.token_hash == "a" * 64
    assert token.expires_at == expires_at
    assert token.revoked_at is None

    session.add.assert_called_once_with(token)
    session.flush.assert_awaited_once()


async def test_get_by_token_hash_returns_token() -> None:
    session = AsyncMock(spec=AsyncSession)

    expected_token = RefreshToken(
        user_id=uuid4(),
        jti=uuid4(),
        token_hash="a" * 64,
        expires_at=datetime.now(UTC) + timedelta(days=7),
    )

    result = Mock()
    result.scalar_one_or_none.return_value = expected_token
    session.execute.return_value = result

    repository = RefreshTokenRepository(session)

    returned_token = await repository.get_by_token_hash("a" * 64)

    assert returned_token is expected_token
    session.execute.assert_awaited_once()


async def test_revoke_marks_token_as_revoked() -> None:
    session = AsyncMock(spec=AsyncSession)
    repository = RefreshTokenRepository(session)

    token = RefreshToken(
        user_id=uuid4(),
        jti=uuid4(),
        token_hash="a" * 64,
        expires_at=datetime.now(UTC) + timedelta(days=7),
    )

    replacement_jti = uuid4()

    await repository.revoke(
        token,
        replaced_by_jti=replacement_jti,
    )

    assert token.revoked_at is not None
    assert token.replaced_by_jti == replacement_jti
    assert token.is_revoked is True

    session.flush.assert_awaited_once()


async def test_refresh_token_is_not_revoked_initially() -> None:
    token = RefreshToken(
        user_id=uuid4(),
        jti=uuid4(),
        token_hash="a" * 64,
        expires_at=datetime.now(UTC) + timedelta(days=7),
    )

    assert token.is_revoked is False
