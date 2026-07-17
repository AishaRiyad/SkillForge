from uuid import UUID

from fastapi import APIRouter, Query, Response, status

from app.api.dependencies import (
    AdminUser,
    CategoryServiceDependency,
)
from app.schemas.category import (
    CategoryCreateRequest,
    CategoryListResponse,
    CategoryResponse,
    CategoryUpdateRequest,
)

router = APIRouter(
    prefix="/categories",
    tags=["Categories"],
)


@router.get(
    "",
    response_model=CategoryListResponse,
    status_code=status.HTTP_200_OK,
    summary="List active categories",
)
async def list_categories(
    category_service: CategoryServiceDependency,
    page: int = Query(
        default=1,
        ge=1,
    ),
    page_size: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
) -> CategoryListResponse:
    return await category_service.list_categories(
        page=page,
        page_size=page_size,
    )


@router.get(
    "/{category_id}",
    response_model=CategoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a category",
)
async def get_category(
    category_id: UUID,
    category_service: CategoryServiceDependency,
) -> CategoryResponse:
    category = await category_service.get_category(category_id)

    return CategoryResponse.model_validate(category)


@router.post(
    "",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a category",
)
async def create_category(
    request: CategoryCreateRequest,
    current_admin: AdminUser,
    category_service: CategoryServiceDependency,
) -> CategoryResponse:
    del current_admin

    category = await category_service.create_category(request)

    return CategoryResponse.model_validate(category)


@router.patch(
    "/{category_id}",
    response_model=CategoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a category",
)
async def update_category(
    category_id: UUID,
    request: CategoryUpdateRequest,
    current_admin: AdminUser,
    category_service: CategoryServiceDependency,
) -> CategoryResponse:
    del current_admin

    category = await category_service.update_category(
        category_id,
        request,
    )

    return CategoryResponse.model_validate(category)


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Soft delete a category",
)
async def delete_category(
    category_id: UUID,
    current_admin: AdminUser,
    category_service: CategoryServiceDependency,
) -> Response:
    del current_admin

    await category_service.delete_category(category_id)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
