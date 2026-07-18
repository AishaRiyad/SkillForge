from uuid import UUID

from fastapi import APIRouter, Response, status

from app.api.dependencies import (
    AdminUser,
    LessonServiceDependency,
)
from app.schemas.lesson import (
    LessonCreateRequest,
    LessonListResponse,
    LessonResponse,
    LessonUpdateRequest,
)

router = APIRouter(
    tags=["Lessons"],
)


@router.get(
    "/courses/{course_id}/lessons",
    response_model=LessonListResponse,
)
async def list_course_lessons(
    course_id: UUID,
    lesson_service: LessonServiceDependency,
) -> LessonListResponse:
    return await lesson_service.list_public_lessons(course_id)


@router.get(
    "/lessons/{lesson_id}",
    response_model=LessonResponse,
)
async def get_lesson(
    lesson_id: UUID,
    lesson_service: LessonServiceDependency,
) -> LessonResponse:
    lesson = await lesson_service.get_public_lesson(lesson_id)

    return LessonResponse.model_validate(lesson)


@router.post(
    "/courses/{course_id}/lessons",
    response_model=LessonResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_lesson(
    course_id: UUID,
    request: LessonCreateRequest,
    current_admin: AdminUser,
    lesson_service: LessonServiceDependency,
) -> LessonResponse:
    del current_admin

    lesson = await lesson_service.create_lesson(
        course_id,
        request,
    )

    return LessonResponse.model_validate(lesson)


@router.patch(
    "/lessons/{lesson_id}",
    response_model=LessonResponse,
)
async def update_lesson(
    lesson_id: UUID,
    request: LessonUpdateRequest,
    current_admin: AdminUser,
    lesson_service: LessonServiceDependency,
) -> LessonResponse:
    del current_admin

    lesson = await lesson_service.update_lesson(
        lesson_id,
        request,
    )

    return LessonResponse.model_validate(lesson)


@router.delete(
    "/lessons/{lesson_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_lesson(
    lesson_id: UUID,
    current_admin: AdminUser,
    lesson_service: LessonServiceDependency,
) -> Response:
    del current_admin

    await lesson_service.delete_lesson(lesson_id)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
