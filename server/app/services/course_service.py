from math import ceil
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    ConflictError,
    ResourceNotFoundError,
)
from app.models.course import Course
from app.repositories.category_repository import CategoryRepository
from app.repositories.course_repository import CourseRepository
from app.schemas.course import (
    CourseCreateRequest,
    CourseListResponse,
    CourseResponse,
    CourseUpdateRequest,
)
from app.utils.slug import generate_slug


class CourseService:
    def __init__(
        self,
        session: AsyncSession,
        course_repository: CourseRepository,
        category_repository: CategoryRepository,
    ) -> None:
        self.session = session
        self.course_repository = course_repository
        self.category_repository = category_repository

    async def create_course(
        self,
        request: CourseCreateRequest,
    ) -> Course:
        await self._ensure_active_category_exists(request.category_id)

        existing_title = await self.course_repository.get_by_title(request.title)

        if existing_title is not None:
            raise ConflictError(
                message="A course with this title already exists.",
                details={"field": "title"},
            )

        slug = generate_slug(request.title)

        if not slug:
            raise ConflictError(
                message=(
                    "A valid course slug could not be generated "
                    "from the supplied title."
                ),
                details={"field": "title"},
            )

        existing_slug = await self.course_repository.get_by_slug(slug)

        if existing_slug is not None:
            raise ConflictError(
                message="A course with this slug already exists.",
                details={"field": "slug"},
            )

        try:
            course = await self.course_repository.create(
                category_id=request.category_id,
                title=request.title,
                slug=slug,
                short_description=request.short_description,
                description=request.description,
                thumbnail_url=request.thumbnail_url,
                estimated_minutes=request.estimated_minutes,
                difficulty_level=request.difficulty_level,
                xp_reward=request.xp_reward,
                price=request.price,
                status=request.status,
            )

            await self.session.commit()
            await self.session.refresh(course)
            await self.session.refresh(
                course,
                attribute_names=["category"],
            )

            return course

        except IntegrityError as exception:
            await self.session.rollback()

            raise ConflictError(
                message="A course with this title or slug already exists.",
            ) from exception

        except Exception:
            await self.session.rollback()
            raise

    async def get_public_course(
        self,
        course_id: UUID,
    ) -> Course:
        course = await self.course_repository.get_by_id(course_id)

        if course is None:
            raise ResourceNotFoundError(
                resource="Course",
                resource_id=str(course_id),
            )

        return course

    async def get_managed_course(
        self,
        course_id: UUID,
    ) -> Course:
        course = await self.course_repository.get_by_id(
            course_id,
            include_inactive=True,
            include_unpublished=True,
        )

        if course is None:
            raise ResourceNotFoundError(
                resource="Course",
                resource_id=str(course_id),
            )

        return course

    async def list_public_courses(
        self,
        *,
        page: int,
        page_size: int,
        category_id: UUID | None,
        difficulty_level: int | None,
    ) -> CourseListResponse:
        offset = (page - 1) * page_size

        courses = await self.course_repository.list_courses(
            offset=offset,
            limit=page_size,
            category_id=category_id,
            difficulty_level=difficulty_level,
        )

        total = await self.course_repository.count(
            category_id=category_id,
            difficulty_level=difficulty_level,
        )

        pages = ceil(total / page_size) if total else 0

        return CourseListResponse(
            items=[CourseResponse.model_validate(course) for course in courses],
            page=page,
            page_size=page_size,
            total=total,
            pages=pages,
        )

    async def update_course(
        self,
        course_id: UUID,
        request: CourseUpdateRequest,
    ) -> Course:
        course = await self.get_managed_course(course_id)

        update_data = request.model_dump(exclude_unset=True)

        if not update_data:
            return course

        requested_category_id = update_data.get("category_id")

        if requested_category_id is not None:
            await self._ensure_active_category_exists(requested_category_id)

        requested_title = update_data.get("title")

        if (
            requested_title is not None
            and requested_title.lower() != course.title.lower()
        ):
            existing_title = await self.course_repository.get_by_title(requested_title)

            if existing_title is not None and existing_title.id != course.id:
                raise ConflictError(
                    message="A course with this title already exists.",
                    details={"field": "title"},
                )

            new_slug = generate_slug(requested_title)

            if not new_slug:
                raise ConflictError(
                    message=(
                        "A valid course slug could not be "
                        "generated from the supplied title."
                    ),
                    details={"field": "title"},
                )

            existing_slug = await self.course_repository.get_by_slug(new_slug)

            if existing_slug is not None and existing_slug.id != course.id:
                raise ConflictError(
                    message="A course with this slug already exists.",
                    details={"field": "slug"},
                )

            update_data["slug"] = new_slug

        try:
            updated_course = await self.course_repository.update(
                course,
                update_data,
            )

            await self.session.commit()
            await self.session.refresh(updated_course)
            await self.session.refresh(
                updated_course,
                attribute_names=["category"],
            )

            return updated_course

        except IntegrityError as exception:
            await self.session.rollback()

            raise ConflictError(
                message="A course with this title or slug already exists.",
            ) from exception

        except Exception:
            await self.session.rollback()
            raise

    async def delete_course(
        self,
        course_id: UUID,
    ) -> None:
        course = await self.get_managed_course(course_id)

        if not course.is_active:
            return

        try:
            await self.course_repository.soft_delete(course)
            await self.session.commit()

        except Exception:
            await self.session.rollback()
            raise

    async def _ensure_active_category_exists(
        self,
        category_id: UUID,
    ) -> None:
        category = await self.category_repository.get_by_id(category_id)

        if category is None:
            raise ResourceNotFoundError(
                resource="Active category",
                resource_id=str(category_id),
            )
