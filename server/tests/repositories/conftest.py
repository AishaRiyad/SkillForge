from collections.abc import AsyncIterator, Iterator
from decimal import Decimal

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings
from app.database.base import Base, import_all_models
from app.main import create_application
from app.models.category import Category
from app.models.course import Course
from app.models.enums import CourseStatus, LessonStatus
from app.models.lesson import Lesson

test_engine = create_async_engine(
    settings.database_url,
    echo=False,
)

TestSessionFactory = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture
def application() -> FastAPI:
    return create_application()


@pytest.fixture
async def client(
    application: FastAPI,
) -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=application)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as async_client:
        yield async_client


@pytest.fixture(autouse=True)
def clear_dependency_overrides(
    application: FastAPI,
) -> Iterator[None]:
    yield
    application.dependency_overrides.clear()


@pytest.fixture
async def db_session() -> AsyncIterator[AsyncSession]:
    import_all_models()

    async with test_engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    async with TestSessionFactory() as session:
        try:
            yield session
        finally:
            await session.rollback()

    async with test_engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def category(
    db_session: AsyncSession,
) -> Category:
    category = Category(
        name="Programming",
        slug="programming",
        is_active=True,
    )

    db_session.add(category)
    await db_session.flush()

    return category


@pytest.fixture
async def course(
    db_session: AsyncSession,
    category: Category,
) -> Course:
    course = Course(
        category_id=category.id,
        title="FastAPI Course",
        slug="fastapi-course",
        short_description="FastAPI test course",
        description=None,
        thumbnail_url=None,
        estimated_minutes=60,
        difficulty_level=1,
        xp_reward=100,
        price=Decimal("0.00"),
        status=CourseStatus.DRAFT,
        is_active=True,
    )

    db_session.add(course)
    await db_session.flush()

    return course


@pytest.fixture
async def lesson(
    db_session: AsyncSession,
    course: Course,
) -> Lesson:
    lesson = Lesson(
        course_id=course.id,
        title="FastAPI Basics",
        slug="fastapi-basics",
        content=None,
        video_url=None,
        estimated_minutes=10,
        position=1,
        is_preview=False,
        status=LessonStatus.DRAFT,
        is_active=True,
    )

    db_session.add(lesson)
    await db_session.flush()

    return lesson
