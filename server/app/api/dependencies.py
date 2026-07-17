from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_database_session
from app.repositories.refresh_token_repository import (
    RefreshTokenRepository,
)
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService

DatabaseSession = Annotated[
    AsyncSession,
    Depends(get_database_session),
]


def get_auth_service(
    session: DatabaseSession,
) -> AuthService:
    user_repository = UserRepository(session)
    refresh_token_repository = RefreshTokenRepository(session)

    return AuthService(
        session=session,
        user_repository=user_repository,
        refresh_token_repository=refresh_token_repository,
    )


AuthServiceDependency = Annotated[
    AuthService,
    Depends(get_auth_service),
]
