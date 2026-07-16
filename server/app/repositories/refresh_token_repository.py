from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.refresh_token import RefreshToken


class RefreshTokenRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        *,
        user_id: UUID,
        jti: UUID,
        token_hash: str,
        expires_at: datetime,
    ) -> RefreshToken:
        refresh_token = RefreshToken(
            user_id=user_id,
            jti=jti,
            token_hash=token_hash,
            expires_at=expires_at,
        )

        self.session.add(refresh_token)
        await self.session.flush()

        return refresh_token

    async def get_by_token_hash(
        self,
        token_hash: str,
    ) -> RefreshToken | None:
        statement = select(RefreshToken).where(RefreshToken.token_hash == token_hash)

        result = await self.session.execute(statement)

        return result.scalar_one_or_none()

    async def get_active_by_token_hash(
        self,
        token_hash: str,
    ) -> RefreshToken | None:
        current_time = datetime.now(UTC)

        statement = select(RefreshToken).where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.revoked_at.is_(None),
            RefreshToken.expires_at > current_time,
        )

        result = await self.session.execute(statement)

        return result.scalar_one_or_none()

    async def revoke(
        self,
        refresh_token: RefreshToken,
        *,
        replaced_by_jti: UUID | None = None,
    ) -> None:
        refresh_token.revoked_at = datetime.now(UTC)
        refresh_token.replaced_by_jti = replaced_by_jti

        await self.session.flush()

    async def revoke_all_for_user(
        self,
        user_id: UUID,
    ) -> int:
        statement = select(RefreshToken).where(
            RefreshToken.user_id == user_id,
            RefreshToken.revoked_at.is_(None),
        )

        result = await self.session.execute(statement)
        tokens = list(result.scalars().all())

        revoked_at = datetime.now(UTC)

        for token in tokens:
            token.revoked_at = revoked_at

        await self.session.flush()

        return len(tokens)
