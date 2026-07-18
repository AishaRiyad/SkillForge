from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query, Response, status

from app.api.dependencies import (
    AdminUser,
    CourseServiceDependency,
)
from app.schemas.course import (
    CourseCreateRequest,
    CourseListResponse,
    CourseResponse,
    CourseUpdateRequest,
)

router = APIRouter(
    prefix="/courses",
    tags=["Courses"],
)


@router.get(
    "",
    response_model=CourseListResponse,
    status_code=status.HTTP_200_OK,
    summary="List published courses",
)
async def list_courses(
    course_service: CourseServiceDependency,
    page: Annotated[
        int,
        Query(ge=1),
    ] = 1,
    page_size: Annotated[
        int,
        Query(ge=1, le=100),
    ] = 20,
    category_id: Annotated[
        UUID | None,
        Query(),
    ] = None,
    difficulty_level: Annotated[
        int | None,
        Query(ge=1, le=5),
    ] = None,
) -> CourseListResponse:
    return await course_service.list_public_courses(
        page=page,
        page_size=page_size,
        category_id=category_id,
        difficulty_level=difficulty_level,
    )


@router.get(
    "/{course_id}",
    response_model=CourseResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a published course",
)
async def get_course(
    course_id: UUID,
    course_service: CourseServiceDependency,
) -> CourseResponse:
    course = await course_service.get_public_course(course_id)

    return CourseResponse.model_validate(course)


@router.post(
    "",
    response_model=CourseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a course",
)
async def create_course(
    request: CourseCreateRequest,
    current_admin: AdminUser,
    course_service: CourseServiceDependency,
) -> CourseResponse:
    del current_admin

    course = await course_service.create_course(request)

    return CourseResponse.model_validate(course)


@router.patch(
    "/{course_id}",
    response_model=CourseResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a course",
)
async def update_course(
    course_id: UUID,
    request: CourseUpdateRequest,
    current_admin: AdminUser,
    course_service: CourseServiceDependency,
) -> CourseResponse:
    del current_admin

    course = await course_service.update_course(
        course_id,
        request,
    )

    return CourseResponse.model_validate(course)


@router.delete(
    "/{course_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Archive a course",
)
async def delete_course(
    course_id: UUID,
    current_admin: AdminUser,
    course_service: CourseServiceDependency,
) -> Response:
    del current_admin

    await course_service.delete_course(course_id)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
