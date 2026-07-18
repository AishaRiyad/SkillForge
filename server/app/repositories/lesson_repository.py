from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import LessonStatus
from app.models.lesson import Lesson


class LessonRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        *,
        course_id: UUID,
        title: str,
        slug: str,
        content: str | None,
        video_url: str | None,
        estimated_minutes: int,
        position: int,
        is_preview: bool,
        status: LessonStatus,
    ) -> Lesson:
        lesson = Lesson(
            course_id=course_id,
            title=title,
            slug=slug,
            content=content,
            video_url=video_url,
            estimated_minutes=estimated_minutes,
            position=position,
            is_preview=is_preview,
            status=status,
            is_active=True,
        )

        self.session.add(lesson)
        await self.session.flush()

        return lesson

    async def get_by_id(
        self,
        lesson_id: UUID,
        *,
        include_inactive: bool = False,
        include_unpublished: bool = False,
    ) -> Lesson | None:
        statement = select(Lesson).where(Lesson.id == lesson_id)

        if not include_inactive:
            statement = statement.where(Lesson.is_active.is_(True))

        if not include_unpublished:
            statement = statement.where(Lesson.status == LessonStatus.PUBLISHED)

        result = await self.session.execute(statement)

        return result.scalar_one_or_none()

    async def get_by_position(
        self,
        *,
        course_id: UUID,
        position: int,
    ) -> Lesson | None:
        statement = select(Lesson).where(
            Lesson.course_id == course_id,
            Lesson.position == position,
        )

        result = await self.session.execute(statement)

        return result.scalar_one_or_none()

    async def get_by_slug(
        self,
        *,
        course_id: UUID,
        slug: str,
    ) -> Lesson | None:
        statement = select(Lesson).where(
            Lesson.course_id == course_id,
            Lesson.slug == slug,
        )

        result = await self.session.execute(statement)

        return result.scalar_one_or_none()

    async def list_by_course(
        self,
        course_id: UUID,
        *,
        include_inactive: bool = False,
        include_unpublished: bool = False,
    ) -> list[Lesson]:
        statement = select(Lesson).where(Lesson.course_id == course_id)

        if not include_inactive:
            statement = statement.where(Lesson.is_active.is_(True))

        if not include_unpublished:
            statement = statement.where(Lesson.status == LessonStatus.PUBLISHED)

        statement = statement.order_by(Lesson.position.asc())

        result = await self.session.execute(statement)

        return list(result.scalars().all())

    async def count_by_course(
        self,
        course_id: UUID,
        *,
        include_inactive: bool = False,
        include_unpublished: bool = False,
    ) -> int:
        statement = select(func.count(Lesson.id)).where(Lesson.course_id == course_id)

        if not include_inactive:
            statement = statement.where(Lesson.is_active.is_(True))

        if not include_unpublished:
            statement = statement.where(Lesson.status == LessonStatus.PUBLISHED)

        result = await self.session.execute(statement)

        return int(result.scalar_one())

    async def update(
        self,
        lesson: Lesson,
        update_data: dict[str, Any],
    ) -> Lesson:
        for field_name, value in update_data.items():
            setattr(lesson, field_name, value)

        await self.session.flush()

        return lesson

    async def soft_delete(
        self,
        lesson: Lesson,
    ) -> Lesson:
        lesson.is_active = False
        lesson.status = LessonStatus.ARCHIVED

        await self.session.flush()

        return lesson
