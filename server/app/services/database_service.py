from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class DatabaseService:
    @staticmethod
    async def check_connection(session: AsyncSession) -> bool:
        result = await session.execute(text("SELECT 1"))

        value = result.scalar_one()

        return bool(value == 1)
