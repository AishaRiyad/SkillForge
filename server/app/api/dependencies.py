from typing import Annotated

from fastapi import Depends, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.core.tokens import get_token_user_id
from app.database.session import get_database_session
from app.models.enums import UserRole, UserStatus
from app.models.user import User
from app.repositories.category_repository import CategoryRepository
from app.repositories.course_repository import CourseRepository
from app.repositories.lesson_repository import LessonRepository
from app.repositories.profile_repository import ProfileRepository
from app.repositories.refresh_token_repository import (
    RefreshTokenRepository,
)
from app.repositories.user_repository import UserRepository
from app.schemas.auth import TokenType
from app.services.auth_service import AuthService
from app.services.category_service import CategoryService
from app.services.course_service import CourseService
from app.services.lesson_service import LessonService
from app.services.user_service import UserService

DatabaseSession = Annotated[
    AsyncSession,
    Depends(get_database_session),
]

bearer_scheme = HTTPBearer(
    scheme_name="BearerAuth",
    description="Enter the JWT access token.",
    auto_error=False,
)


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


def get_user_service(
    session: DatabaseSession,
) -> UserService:
    profile_repository = ProfileRepository(session)

    return UserService(
        session=session,
        profile_repository=profile_repository,
    )


UserServiceDependency = Annotated[
    UserService,
    Depends(get_user_service),
]


async def get_current_user(
    session: DatabaseSession,
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Security(bearer_scheme),
    ],
) -> User:
    if credentials is None:
        raise UnauthorizedError(message="A valid access token is required.")

    if credentials.scheme.lower() != "bearer":
        raise UnauthorizedError(message="The authentication scheme must be Bearer.")

    user_id = get_token_user_id(
        credentials.credentials,
        expected_type=TokenType.ACCESS,
    )

    repository = UserRepository(session)
    user = await repository.get_by_id(user_id)

    if user is None:
        raise UnauthorizedError(message="The authenticated user no longer exists.")

    return user


CurrentUser = Annotated[
    User,
    Depends(get_current_user),
]


async def get_active_user(
    current_user: CurrentUser,
) -> User:
    if current_user.status != UserStatus.ACTIVE:
        raise UnauthorizedError(message="This account is not active.")

    return current_user


ActiveUser = Annotated[
    User,
    Depends(get_active_user),
]


async def require_admin(
    current_user: ActiveUser,
) -> User:
    if current_user.role != UserRole.ADMIN:
        raise ForbiddenError(message="Administrator permission is required.")

    return current_user


AdminUser = Annotated[
    User,
    Depends(require_admin),
]


async def require_moderator_or_admin(
    current_user: ActiveUser,
) -> User:
    allowed_roles = {
        UserRole.MODERATOR,
        UserRole.ADMIN,
    }

    if current_user.role not in allowed_roles:
        raise ForbiddenError(
            message="Moderator or administrator permission is required."
        )

    return current_user


ModeratorOrAdmin = Annotated[
    User,
    Depends(require_moderator_or_admin),
]


def get_category_service(
    session: DatabaseSession,
) -> CategoryService:
    repository = CategoryRepository(session)

    return CategoryService(
        session=session,
        category_repository=repository,
    )


CategoryServiceDependency = Annotated[
    CategoryService,
    Depends(get_category_service),
]


def get_course_service(
    session: DatabaseSession,
) -> CourseService:
    course_repository = CourseRepository(session)
    category_repository = CategoryRepository(session)

    return CourseService(
        session=session,
        course_repository=course_repository,
        category_repository=category_repository,
    )


CourseServiceDependency = Annotated[
    CourseService,
    Depends(get_course_service),
]


def get_lesson_service(
    session: DatabaseSession,
) -> LessonService:
    return LessonService(
        session=session,
        lesson_repository=LessonRepository(session),
        course_repository=CourseRepository(session),
    )


LessonServiceDependency = Annotated[
    LessonService,
    Depends(get_lesson_service),
]
