from math import ceil
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    ConflictError,
    ResourceNotFoundError,
)
from app.models.category import Category
from app.repositories.category_repository import CategoryRepository
from app.schemas.category import (
    CategoryCreateRequest,
    CategoryListResponse,
    CategoryResponse,
    CategoryUpdateRequest,
)
from app.utils.slug import generate_slug


class CategoryService:
    def __init__(
        self,
        session: AsyncSession,
        category_repository: CategoryRepository,
    ) -> None:
        self.session = session
        self.category_repository = category_repository

    async def create_category(
        self,
        request: CategoryCreateRequest,
    ) -> Category:
        existing_name = await self.category_repository.get_by_name(request.name)

        if existing_name is not None:
            raise ConflictError(
                message="A category with this name already exists.",
                details={"field": "name"},
            )

        slug = generate_slug(request.name)

        if not slug:
            raise ConflictError(
                message=(
                    "A valid category slug could not be generated "
                    "from the supplied name."
                ),
                details={"field": "name"},
            )

        existing_slug = await self.category_repository.get_by_slug(slug)

        if existing_slug is not None:
            raise ConflictError(
                message="A category with this slug already exists.",
                details={"field": "slug"},
            )

        try:
            category = await self.category_repository.create(
                name=request.name,
                slug=slug,
                description=request.description,
                icon=request.icon,
            )

            await self.session.commit()
            await self.session.refresh(category)

            return category

        except IntegrityError as exception:
            await self.session.rollback()

            raise ConflictError(
                message=("A category with this name or slug already exists."),
            ) from exception

        except Exception:
            await self.session.rollback()
            raise

    async def get_category(
        self,
        category_id: UUID,
        *,
        include_inactive: bool = False,
    ) -> Category:
        category = await self.category_repository.get_by_id(
            category_id,
            include_inactive=include_inactive,
        )

        if category is None:
            raise ResourceNotFoundError(
                resource="Category",
                resource_id=str(category_id),
            )

        return category

    async def list_categories(
        self,
        *,
        page: int,
        page_size: int,
        include_inactive: bool = False,
    ) -> CategoryListResponse:
        offset = (page - 1) * page_size

        categories = await self.category_repository.list_categories(
            offset=offset,
            limit=page_size,
            include_inactive=include_inactive,
        )

        total = await self.category_repository.count(include_inactive=include_inactive)

        pages = ceil(total / page_size) if total else 0

        return CategoryListResponse(
            items=[
                CategoryResponse.model_validate(category) for category in categories
            ],
            page=page,
            page_size=page_size,
            total=total,
            pages=pages,
        )

    async def update_category(
        self,
        category_id: UUID,
        request: CategoryUpdateRequest,
    ) -> Category:
        category = await self.get_category(
            category_id,
            include_inactive=True,
        )

        update_data = request.model_dump(exclude_unset=True)

        if not update_data:
            return category

        requested_name = update_data.get("name")

        if (
            requested_name is not None
            and requested_name.lower() != category.name.lower()
        ):
            existing_name = await self.category_repository.get_by_name(requested_name)

            if existing_name is not None and existing_name.id != category.id:
                raise ConflictError(
                    message="A category with this name already exists.",
                    details={"field": "name"},
                )

            new_slug = generate_slug(requested_name)

            if not new_slug:
                raise ConflictError(
                    message=(
                        "A valid category slug could not be "
                        "generated from the supplied name."
                    ),
                    details={"field": "name"},
                )

            existing_slug = await self.category_repository.get_by_slug(new_slug)

            if existing_slug is not None and existing_slug.id != category.id:
                raise ConflictError(
                    message="A category with this slug already exists.",
                    details={"field": "slug"},
                )

            update_data["slug"] = new_slug

        try:
            updated_category = await self.category_repository.update(
                category,
                update_data,
            )

            await self.session.commit()
            await self.session.refresh(updated_category)

            return updated_category

        except IntegrityError as exception:
            await self.session.rollback()

            raise ConflictError(
                message=("A category with this name or slug already exists."),
            ) from exception

        except Exception:
            await self.session.rollback()
            raise

    async def delete_category(
        self,
        category_id: UUID,
    ) -> None:
        category = await self.get_category(
            category_id,
            include_inactive=True,
        )

        if not category.is_active:
            return

        try:
            await self.category_repository.soft_delete(category)
            await self.session.commit()

        except Exception:
            await self.session.rollback()
            raise
