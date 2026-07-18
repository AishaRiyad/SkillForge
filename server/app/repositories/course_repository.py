from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.course import Course
from app.models.enums import CourseStatus


class CourseRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        *,
        category_id: UUID,
        title: str,
        slug: str,
        short_description: str | None,
        description: str | None,
        thumbnail_url: str | None,
        estimated_minutes: int,
        difficulty_level: int,
        xp_reward: int,
        price: Decimal,
        status: CourseStatus,
    ) -> Course:
        course = Course(
            category_id=category_id,
            title=title,
            slug=slug,
            short_description=short_description,
            description=description,
            thumbnail_url=thumbnail_url,
            estimated_minutes=estimated_minutes,
            difficulty_level=difficulty_level,
            xp_reward=xp_reward,
            price=price,
            status=status,
            is_active=True,
        )

        self.session.add(course)
        await self.session.flush()

        return course

    async def get_by_id(
        self,
        course_id: UUID,
        *,
        include_inactive: bool = False,
        include_unpublished: bool = False,
    ) -> Course | None:
        statement = (
            select(Course)
            .options(selectinload(Course.category))
            .where(Course.id == course_id)
        )

        if not include_inactive:
            statement = statement.where(Course.is_active.is_(True))

        if not include_unpublished:
            statement = statement.where(Course.status == CourseStatus.PUBLISHED)

        result = await self.session.execute(statement)

        return result.scalar_one_or_none()

    async def get_by_title(
        self,
        title: str,
    ) -> Course | None:
        normalized_title = title.strip().lower()

        statement = select(Course).where(func.lower(Course.title) == normalized_title)

        result = await self.session.execute(statement)

        return result.scalar_one_or_none()

    async def get_by_slug(
        self,
        slug: str,
    ) -> Course | None:
        statement = select(Course).where(Course.slug == slug)

        result = await self.session.execute(statement)

        return result.scalar_one_or_none()

    async def list_courses(
        self,
        *,
        offset: int,
        limit: int,
        category_id: UUID | None = None,
        difficulty_level: int | None = None,
        include_inactive: bool = False,
        include_unpublished: bool = False,
    ) -> list[Course]:
        statement = select(Course).options(selectinload(Course.category))

        if category_id is not None:
            statement = statement.where(Course.category_id == category_id)

        if difficulty_level is not None:
            statement = statement.where(Course.difficulty_level == difficulty_level)

        if not include_inactive:
            statement = statement.where(Course.is_active.is_(True))

        if not include_unpublished:
            statement = statement.where(Course.status == CourseStatus.PUBLISHED)

        statement = (
            statement.order_by(Course.created_at.desc()).offset(offset).limit(limit)
        )

        result = await self.session.execute(statement)

        return list(result.scalars().all())

    async def count(
        self,
        *,
        category_id: UUID | None = None,
        difficulty_level: int | None = None,
        include_inactive: bool = False,
        include_unpublished: bool = False,
    ) -> int:
        statement = select(func.count(Course.id))

        if category_id is not None:
            statement = statement.where(Course.category_id == category_id)

        if difficulty_level is not None:
            statement = statement.where(Course.difficulty_level == difficulty_level)

        if not include_inactive:
            statement = statement.where(Course.is_active.is_(True))

        if not include_unpublished:
            statement = statement.where(Course.status == CourseStatus.PUBLISHED)

        result = await self.session.execute(statement)

        return int(result.scalar_one())

    async def update(
        self,
        course: Course,
        update_data: dict[str, Any],
    ) -> Course:
        for field_name, value in update_data.items():
            setattr(course, field_name, value)

        await self.session.flush()

        return course

    async def soft_delete(
        self,
        course: Course,
    ) -> Course:
        course.is_active = False
        course.status = CourseStatus.ARCHIVED

        await self.session.flush()

        return course
