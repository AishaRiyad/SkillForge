from datetime import UTC, datetime
from decimal import Decimal
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError
from app.models.category import Category
from app.models.course import Course
from app.models.enums import CourseStatus
from app.repositories.category_repository import CategoryRepository
from app.repositories.course_repository import CourseRepository
from app.schemas.course import (
    CourseCreateRequest,
    CourseUpdateRequest,
)
from app.services.course_service import CourseService


def create_category() -> Category:
    now = datetime.now(UTC)

    category = Category(
        name="Backend",
        slug="backend",
        is_active=True,
    )
    category.id = uuid4()
    category.created_at = now
    category.updated_at = now

    return category


def create_course(category: Category) -> Course:
    now = datetime.now(UTC)

    course = Course(
        category_id=category.id,
        title="FastAPI Fundamentals",
        slug="fastapi-fundamentals",
        estimated_minutes=120,
        difficulty_level=2,
        xp_reward=500,
        price=Decimal("0.00"),
        status=CourseStatus.PUBLISHED,
        is_active=True,
    )

    course.id = uuid4()
    course.category = category
    course.created_at = now
    course.updated_at = now

    return course


async def test_create_course_commits() -> None:
    session = AsyncMock(spec=AsyncSession)
    course_repository = AsyncMock(spec=CourseRepository)
    category_repository = AsyncMock(spec=CategoryRepository)

    category = create_category()
    course = create_course(category)

    category_repository.get_by_id.return_value = category
    course_repository.get_by_title.return_value = None
    course_repository.get_by_slug.return_value = None
    course_repository.create.return_value = course

    service = CourseService(
        session=session,
        course_repository=course_repository,
        category_repository=category_repository,
    )

    result = await service.create_course(
        CourseCreateRequest(
            category_id=category.id,
            title="FastAPI Fundamentals",
            estimated_minutes=120,
            difficulty_level=2,
            xp_reward=500,
            status=CourseStatus.PUBLISHED,
        )
    )

    assert result is course
    session.commit.assert_awaited_once()


async def test_create_course_rejects_duplicate_title() -> None:
    session = AsyncMock(spec=AsyncSession)
    course_repository = AsyncMock(spec=CourseRepository)
    category_repository = AsyncMock(spec=CategoryRepository)

    category = create_category()
    course = create_course(category)

    category_repository.get_by_id.return_value = category
    course_repository.get_by_title.return_value = course

    service = CourseService(
        session=session,
        course_repository=course_repository,
        category_repository=category_repository,
    )

    with pytest.raises(ConflictError):
        await service.create_course(
            CourseCreateRequest(
                category_id=category.id,
                title="FastAPI Fundamentals",
            )
        )

    course_repository.create.assert_not_awaited()
    session.commit.assert_not_awaited()


async def test_update_course_changes_slug() -> None:
    session = AsyncMock(spec=AsyncSession)
    course_repository = AsyncMock(spec=CourseRepository)
    category_repository = AsyncMock(spec=CategoryRepository)

    category = create_category()
    course = create_course(category)

    course_repository.get_by_id.return_value = course
    course_repository.get_by_title.return_value = None
    course_repository.get_by_slug.return_value = None
    course_repository.update.return_value = course

    service = CourseService(
        session=session,
        course_repository=course_repository,
        category_repository=category_repository,
    )

    await service.update_course(
        course.id,
        CourseUpdateRequest(
            title="Advanced FastAPI",
        ),
    )

    course_repository.update.assert_awaited_once_with(
        course,
        {
            "title": "Advanced FastAPI",
            "slug": "advanced-fastapi",
        },
    )

    session.commit.assert_awaited_once()


async def test_delete_course_archives_course() -> None:
    session = AsyncMock(spec=AsyncSession)
    course_repository = AsyncMock(spec=CourseRepository)
    category_repository = AsyncMock(spec=CategoryRepository)

    category = create_category()
    course = create_course(category)

    course_repository.get_by_id.return_value = course

    service = CourseService(
        session=session,
        course_repository=course_repository,
        category_repository=category_repository,
    )

    await service.delete_course(course.id)

    course_repository.soft_delete.assert_awaited_once_with(course)
    session.commit.assert_awaited_once()
