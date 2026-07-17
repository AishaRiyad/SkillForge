from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category


class CategoryRepository:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self.session = session

    async def create(
        self,
        *,
        name: str,
        slug: str,
        description: str | None = None,
        icon: str | None = None,
    ) -> Category:
        category = Category(
            name=name,
            slug=slug,
            description=description,
            icon=icon,
            is_active=True,
        )

        self.session.add(category)
        await self.session.flush()

        return category

    async def get_by_id(
        self,
        category_id: UUID,
        *,
        include_inactive: bool = False,
    ) -> Category | None:
        statement = select(Category).where(
            Category.id == category_id,
        )

        if not include_inactive:
            statement = statement.where(
                Category.is_active.is_(True),
            )

        result = await self.session.execute(statement)

        return result.scalar_one_or_none()

    async def get_by_name(
        self,
        name: str,
    ) -> Category | None:
        statement = select(Category).where(
            func.lower(Category.name) == name.lower(),
        )

        result = await self.session.execute(statement)

        return result.scalar_one_or_none()

    async def get_by_slug(
        self,
        slug: str,
    ) -> Category | None:
        statement = select(Category).where(
            Category.slug == slug,
        )

        result = await self.session.execute(statement)

        return result.scalar_one_or_none()

    async def list_categories(
        self,
        *,
        offset: int,
        limit: int,
        include_inactive: bool = False,
    ) -> list[Category]:
        statement = select(Category).order_by(Category.name)

        if not include_inactive:
            statement = statement.where(
                Category.is_active.is_(True),
            )

        statement = statement.offset(offset).limit(limit)

        result = await self.session.execute(statement)

        return list(result.scalars().all())

    async def count(
        self,
        *,
        include_inactive: bool = False,
    ) -> int:
        statement = select(func.count()).select_from(Category)

        if not include_inactive:
            statement = statement.where(
                Category.is_active.is_(True),
            )

        result = await self.session.execute(statement)

        return int(result.scalar_one())

    async def update(
        self,
        category: Category,
        update_data: dict[str, object],
    ) -> Category:
        for field_name, value in update_data.items():
            setattr(category, field_name, value)

        await self.session.flush()

        return category

    async def soft_delete(
        self,
        category: Category,
    ) -> Category:
        category.is_active = False

        await self.session.flush()

        return category
