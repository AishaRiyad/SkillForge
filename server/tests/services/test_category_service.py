from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError
from app.models.category import Category
from app.repositories.category_repository import CategoryRepository
from app.schemas.category import (
    CategoryCreateRequest,
    CategoryUpdateRequest,
)
from app.services.category_service import CategoryService


def create_category() -> Category:
    current_time = datetime.now(UTC)

    category = Category(
        name="Machine Learning",
        slug="machine-learning",
        description="Learn ML",
        icon="brain",
        is_active=True,
    )

    category.id = uuid4()
    category.created_at = current_time
    category.updated_at = current_time

    return category


async def test_create_category_commits() -> None:
    session = AsyncMock(spec=AsyncSession)
    repository = AsyncMock(spec=CategoryRepository)

    category = create_category()

    repository.get_by_name.return_value = None
    repository.get_by_slug.return_value = None
    repository.create.return_value = category

    service = CategoryService(
        session=session,
        category_repository=repository,
    )

    result = await service.create_category(
        CategoryCreateRequest(
            name="Machine Learning",
            description="Learn ML",
            icon="brain",
        )
    )

    assert result is category

    repository.create.assert_awaited_once_with(
        name="Machine Learning",
        slug="machine-learning",
        description="Learn ML",
        icon="brain",
    )

    session.commit.assert_awaited_once()
    session.refresh.assert_awaited_once_with(category)


async def test_create_category_rejects_duplicate_name() -> None:
    session = AsyncMock(spec=AsyncSession)
    repository = AsyncMock(spec=CategoryRepository)

    repository.get_by_name.return_value = create_category()

    service = CategoryService(
        session=session,
        category_repository=repository,
    )

    with pytest.raises(ConflictError):
        await service.create_category(CategoryCreateRequest(name="Machine Learning"))

    repository.create.assert_not_awaited()
    session.commit.assert_not_awaited()


async def test_update_category_generates_new_slug() -> None:
    session = AsyncMock(spec=AsyncSession)
    repository = AsyncMock(spec=CategoryRepository)

    category = create_category()

    repository.get_by_id.return_value = category
    repository.get_by_name.return_value = None
    repository.get_by_slug.return_value = None
    repository.update.return_value = category

    service = CategoryService(
        session=session,
        category_repository=repository,
    )

    await service.update_category(
        category.id,
        CategoryUpdateRequest(name="Artificial Intelligence"),
    )

    repository.update.assert_awaited_once_with(
        category,
        {
            "name": "Artificial Intelligence",
            "slug": "artificial-intelligence",
        },
    )

    session.commit.assert_awaited_once()


async def test_delete_category_uses_soft_delete() -> None:
    session = AsyncMock(spec=AsyncSession)
    repository = AsyncMock(spec=CategoryRepository)

    category = create_category()
    repository.get_by_id.return_value = category

    service = CategoryService(
        session=session,
        category_repository=repository,
    )

    await service.delete_category(category.id)

    repository.soft_delete.assert_awaited_once_with(category)
    session.commit.assert_awaited_once()
