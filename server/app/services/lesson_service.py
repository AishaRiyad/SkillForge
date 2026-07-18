from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    ConflictError,
    ResourceNotFoundError,
)
from app.models.lesson import Lesson
from app.repositories.course_repository import CourseRepository
from app.repositories.lesson_repository import LessonRepository
from app.schemas.lesson import (
    LessonCreateRequest,
    LessonListResponse,
    LessonResponse,
    LessonUpdateRequest,
)
from app.utils.slug import generate_slug


class LessonService:
    def __init__(
        self,
        session: AsyncSession,
        lesson_repository: LessonRepository,
        course_repository: CourseRepository,
    ) -> None:
        self.session = session
        self.lesson_repository = lesson_repository
        self.course_repository = course_repository

    async def create_lesson(
        self,
        course_id: UUID,
        request: LessonCreateRequest,
    ) -> Lesson:
        await self._ensure_course_exists(course_id)

        existing_position = await self.lesson_repository.get_by_position(
            course_id=course_id,
            position=request.position,
        )

        if existing_position is not None:
            raise ConflictError(
                message=("A lesson with this position already exists in the course."),
                details={"field": "position"},
            )

        slug = generate_slug(request.title)

        if not slug:
            raise ConflictError(
                message="A valid lesson slug could not be generated.",
                details={"field": "title"},
            )

        existing_slug = await self.lesson_repository.get_by_slug(
            course_id=course_id,
            slug=slug,
        )

        if existing_slug is not None:
            raise ConflictError(
                message=("A lesson with this title already exists in the course."),
                details={"field": "title"},
            )

        try:
            lesson = await self.lesson_repository.create(
                course_id=course_id,
                title=request.title,
                slug=slug,
                content=request.content,
                video_url=request.video_url,
                estimated_minutes=request.estimated_minutes,
                position=request.position,
                is_preview=request.is_preview,
                status=request.status,
            )

            await self.session.commit()
            await self.session.refresh(lesson)

            return lesson

        except IntegrityError as exception:
            await self.session.rollback()

            raise ConflictError(
                message=("The lesson position or slug already exists in this course."),
            ) from exception

        except Exception:
            await self.session.rollback()
            raise

    async def get_public_lesson(
        self,
        lesson_id: UUID,
    ) -> Lesson:
        lesson = await self.lesson_repository.get_by_id(lesson_id)

        if lesson is None:
            raise ResourceNotFoundError(
                resource="Lesson",
                resource_id=str(lesson_id),
            )

        return lesson

    async def get_managed_lesson(
        self,
        lesson_id: UUID,
    ) -> Lesson:
        lesson = await self.lesson_repository.get_by_id(
            lesson_id,
            include_inactive=True,
            include_unpublished=True,
        )

        if lesson is None:
            raise ResourceNotFoundError(
                resource="Lesson",
                resource_id=str(lesson_id),
            )

        return lesson

    async def list_public_lessons(
        self,
        course_id: UUID,
    ) -> LessonListResponse:
        await self._ensure_course_exists(course_id)

        lessons = await self.lesson_repository.list_by_course(course_id)

        total = await self.lesson_repository.count_by_course(course_id)

        return LessonListResponse(
            items=[LessonResponse.model_validate(lesson) for lesson in lessons],
            total=total,
        )

    async def update_lesson(
        self,
        lesson_id: UUID,
        request: LessonUpdateRequest,
    ) -> Lesson:
        lesson = await self.get_managed_lesson(lesson_id)

        update_data = request.model_dump(exclude_unset=True)

        if not update_data:
            return lesson

        requested_position = update_data.get("position")

        if requested_position is not None and requested_position != lesson.position:
            existing_position = await self.lesson_repository.get_by_position(
                course_id=lesson.course_id,
                position=requested_position,
            )

            if existing_position is not None and existing_position.id != lesson.id:
                raise ConflictError(
                    message=(
                        "A lesson with this position already exists in the course."
                    ),
                    details={"field": "position"},
                )

        requested_title = update_data.get("title")

        if (
            requested_title is not None
            and requested_title.lower() != lesson.title.lower()
        ):
            slug = generate_slug(requested_title)

            if not slug:
                raise ConflictError(
                    message=("A valid lesson slug could not be generated."),
                    details={"field": "title"},
                )

            existing_slug = await self.lesson_repository.get_by_slug(
                course_id=lesson.course_id,
                slug=slug,
            )

            if existing_slug is not None and existing_slug.id != lesson.id:
                raise ConflictError(
                    message=("A lesson with this title already exists in the course."),
                    details={"field": "title"},
                )

            update_data["slug"] = slug

        try:
            updated_lesson = await self.lesson_repository.update(
                lesson,
                update_data,
            )

            await self.session.commit()
            await self.session.refresh(updated_lesson)

            return updated_lesson

        except IntegrityError as exception:
            await self.session.rollback()

            raise ConflictError(
                message=("The lesson position or slug already exists in this course."),
            ) from exception

        except Exception:
            await self.session.rollback()
            raise

    async def delete_lesson(
        self,
        lesson_id: UUID,
    ) -> None:
        lesson = await self.get_managed_lesson(lesson_id)

        if not lesson.is_active:
            return

        try:
            await self.lesson_repository.soft_delete(lesson)
            await self.session.commit()

        except Exception:
            await self.session.rollback()
            raise

    async def _ensure_course_exists(
        self,
        course_id: UUID,
    ) -> None:
        course = await self.course_repository.get_by_id(
            course_id,
            include_inactive=False,
            include_unpublished=True,
        )

        if course is None:
            raise ResourceNotFoundError(
                resource="Active course",
                resource_id=str(course_id),
            )
