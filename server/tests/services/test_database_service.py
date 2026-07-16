from unittest.mock import AsyncMock, Mock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.database_service import DatabaseService


@pytest.mark.parametrize(
    ("database_value", "expected_result"),
    [
        (1, True),
        (0, False),
    ],
)
async def test_check_connection_returns_expected_result(
    database_value: int,
    expected_result: bool,
) -> None:
    session = AsyncMock(spec=AsyncSession)

    result = Mock()
    result.scalar_one.return_value = database_value
    session.execute.return_value = result

    connection_status = await DatabaseService.check_connection(session)

    assert connection_status is expected_result
    session.execute.assert_awaited_once()
