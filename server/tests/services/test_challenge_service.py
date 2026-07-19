from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.core.exceptions import ResourceNotFoundError
from app.models.enums import ChallengeStatus
from app.schemas.challenge import (
    ChallengeCreateRequest,
    ChallengeUpdateRequest,
)
from app.services.challenge_service import ChallengeService


@pytest.fixture
def session() -> AsyncMock:
    mock = AsyncMock()
    mock.commit = AsyncMock()
    mock.rollback = AsyncMock()
    mock.refresh = AsyncMock()

    return mock


@pytest.fixture
def challenge_repository() -> AsyncMock:
    repository = AsyncMock()
    repository.create = AsyncMock()
    repository.get_by_id = AsyncMock()
    repository.list_by_lesson = AsyncMock()
    repository.count_by_lesson = AsyncMock()
    repository.update = AsyncMock()
    repository.soft_delete = AsyncMock()

    return repository


@pytest.fixture
def lesson_repository() -> AsyncMock:
    repository = AsyncMock()
    repository.get_by_id = AsyncMock()

    return repository


@pytest.fixture
def challenge_service(
    session: AsyncMock,
    challenge_repository: AsyncMock,
    lesson_repository: AsyncMock,
) -> ChallengeService:
    return ChallengeService(
        session=session,
        challenge_repository=challenge_repository,
        lesson_repository=lesson_repository,
    )


@pytest.mark.asyncio
async def test_create_challenge_successfully(
    challenge_service: ChallengeService,
    session: AsyncMock,
    challenge_repository: AsyncMock,
    lesson_repository: AsyncMock,
) -> None:
    lesson_id = uuid4()
    challenge_id = uuid4()
    now = datetime.now(UTC)

    lesson_repository.get_by_id.return_value = SimpleNamespace(
        id=lesson_id,
        is_active=True,
    )

    challenge = SimpleNamespace(
        id=challenge_id,
        lesson_id=lesson_id,
        title="FastAPI Quiz",
        description=None,
        passing_score=70,
        xp_reward=100,
        max_attempts=3,
        status=ChallengeStatus.DRAFT,
        is_active=True,
        created_at=now,
        updated_at=now,
    )

    challenge_repository.create.return_value = challenge

    request = ChallengeCreateRequest(
        title="FastAPI Quiz",
        passing_score=70,
        xp_reward=100,
        max_attempts=3,
    )

    result = await challenge_service.create_challenge(
        lesson_id,
        request,
    )

    assert result == challenge

    lesson_repository.get_by_id.assert_awaited_once_with(
        lesson_id,
        include_inactive=False,
        include_unpublished=True,
    )

    challenge_repository.create.assert_awaited_once_with(
        lesson_id=lesson_id,
        title="FastAPI Quiz",
        description=None,
        passing_score=70,
        xp_reward=100,
        max_attempts=3,
        status=ChallengeStatus.DRAFT,
    )

    session.commit.assert_awaited_once()
    session.refresh.assert_awaited_once_with(challenge)
    session.rollback.assert_not_awaited()


@pytest.mark.asyncio
async def test_create_challenge_rejects_missing_lesson(
    challenge_service: ChallengeService,
    session: AsyncMock,
    challenge_repository: AsyncMock,
    lesson_repository: AsyncMock,
) -> None:
    lesson_id = uuid4()

    lesson_repository.get_by_id.return_value = None

    request = ChallengeCreateRequest(
        title="FastAPI Quiz",
    )

    with pytest.raises(ResourceNotFoundError):
        await challenge_service.create_challenge(
            lesson_id,
            request,
        )

    challenge_repository.create.assert_not_awaited()
    session.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_get_managed_challenge_returns_draft_challenge(
    challenge_service: ChallengeService,
    challenge_repository: AsyncMock,
) -> None:
    challenge_id = uuid4()

    challenge = SimpleNamespace(
        id=challenge_id,
        status=ChallengeStatus.DRAFT,
        is_active=True,
    )

    challenge_repository.get_by_id.return_value = challenge

    result = await challenge_service.get_managed_challenge(challenge_id)

    assert result == challenge

    challenge_repository.get_by_id.assert_awaited_once_with(
        challenge_id,
        include_inactive=True,
        include_unpublished=True,
    )


@pytest.mark.asyncio
async def test_get_public_challenge_rejects_draft_or_missing_challenge(
    challenge_service: ChallengeService,
    challenge_repository: AsyncMock,
) -> None:
    challenge_id = uuid4()

    challenge_repository.get_by_id.return_value = None

    with pytest.raises(ResourceNotFoundError):
        await challenge_service.get_public_challenge(challenge_id)


@pytest.mark.asyncio
async def test_update_challenge_successfully(
    challenge_service: ChallengeService,
    session: AsyncMock,
    challenge_repository: AsyncMock,
) -> None:
    challenge_id = uuid4()

    challenge = SimpleNamespace(
        id=challenge_id,
        title="Old Quiz",
        passing_score=70,
        is_active=True,
    )

    challenge_repository.get_by_id.return_value = challenge
    challenge_repository.update.return_value = challenge

    request = ChallengeUpdateRequest(
        title="Updated Quiz",
        passing_score=80,
    )

    result = await challenge_service.update_challenge(
        challenge_id,
        request,
    )

    assert result == challenge

    challenge_repository.update.assert_awaited_once_with(
        challenge,
        {
            "title": "Updated Quiz",
            "passing_score": 80,
        },
    )

    session.commit.assert_awaited_once()
    session.refresh.assert_awaited_once_with(challenge)


@pytest.mark.asyncio
async def test_delete_challenge_soft_deletes_challenge(
    challenge_service: ChallengeService,
    session: AsyncMock,
    challenge_repository: AsyncMock,
) -> None:
    challenge_id = uuid4()

    challenge = SimpleNamespace(
        id=challenge_id,
        is_active=True,
        status=ChallengeStatus.PUBLISHED,
    )

    challenge_repository.get_by_id.return_value = challenge
    challenge_repository.soft_delete.return_value = challenge

    await challenge_service.delete_challenge(challenge_id)

    challenge_repository.soft_delete.assert_awaited_once_with(challenge)

    session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_inactive_challenge_is_idempotent(
    challenge_service: ChallengeService,
    session: AsyncMock,
    challenge_repository: AsyncMock,
) -> None:
    challenge_id = uuid4()

    challenge = SimpleNamespace(
        id=challenge_id,
        is_active=False,
        status=ChallengeStatus.ARCHIVED,
    )

    challenge_repository.get_by_id.return_value = challenge

    await challenge_service.delete_challenge(challenge_id)

    challenge_repository.soft_delete.assert_not_awaited()
    session.commit.assert_not_awaited()
