from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.core.exceptions import ConflictError, ResourceNotFoundError
from app.models.enums import ChallengeStatus, QuestionType
from app.schemas.question import (
    QuestionCreateRequest,
    QuestionUpdateRequest,
)
from app.services.question_service import QuestionService


@pytest.fixture
def session() -> AsyncMock:
    mock = AsyncMock()
    mock.commit = AsyncMock()
    mock.rollback = AsyncMock()
    mock.refresh = AsyncMock()

    return mock


@pytest.fixture
def question_repository() -> AsyncMock:
    repository = AsyncMock()
    repository.create = AsyncMock()
    repository.get_by_id = AsyncMock()
    repository.get_by_position = AsyncMock()
    repository.list_by_challenge = AsyncMock()
    repository.count_by_challenge = AsyncMock()
    repository.update = AsyncMock()
    repository.soft_delete = AsyncMock()

    return repository


@pytest.fixture
def challenge_repository() -> AsyncMock:
    repository = AsyncMock()
    repository.get_by_id = AsyncMock()

    return repository


@pytest.fixture
def question_service(
    session: AsyncMock,
    question_repository: AsyncMock,
    challenge_repository: AsyncMock,
) -> QuestionService:
    return QuestionService(
        session=session,
        question_repository=question_repository,
        challenge_repository=challenge_repository,
    )


@pytest.mark.asyncio
async def test_create_multiple_choice_question_successfully(
    question_service: QuestionService,
    session: AsyncMock,
    question_repository: AsyncMock,
    challenge_repository: AsyncMock,
) -> None:
    challenge_id = uuid4()
    question_id = uuid4()
    now = datetime.now(UTC)

    challenge_repository.get_by_id.return_value = SimpleNamespace(
        id=challenge_id,
        status=ChallengeStatus.DRAFT,
        is_active=True,
    )

    question_repository.get_by_position.return_value = None

    question = SimpleNamespace(
        id=question_id,
        challenge_id=challenge_id,
        text="Which language is FastAPI built for?",
        question_type=QuestionType.MULTIPLE_CHOICE,
        options=[
            {
                "key": "a",
                "text": "Python",
            },
            {
                "key": "b",
                "text": "Java",
            },
        ],
        correct_answer="a",
        explanation=None,
        position=1,
        points=1,
        is_active=True,
        created_at=now,
        updated_at=now,
    )

    question_repository.create.return_value = question

    request = QuestionCreateRequest(
        text="Which language is FastAPI built for?",
        question_type=QuestionType.MULTIPLE_CHOICE,
        options=[
            {
                "key": "a",
                "text": "Python",
            },
            {
                "key": "b",
                "text": "Java",
            },
        ],
        correct_answer="A",
        position=1,
    )

    result = await question_service.create_question(
        challenge_id,
        request,
    )

    assert result == question

    question_repository.create.assert_awaited_once_with(
        challenge_id=challenge_id,
        text="Which language is FastAPI built for?",
        question_type=QuestionType.MULTIPLE_CHOICE,
        options=[
            {
                "key": "a",
                "text": "Python",
            },
            {
                "key": "b",
                "text": "Java",
            },
        ],
        correct_answer="a",
        explanation=None,
        position=1,
        points=1,
    )

    session.commit.assert_awaited_once()
    session.refresh.assert_awaited_once_with(question)


@pytest.mark.asyncio
async def test_create_question_rejects_duplicate_position(
    question_service: QuestionService,
    session: AsyncMock,
    question_repository: AsyncMock,
    challenge_repository: AsyncMock,
) -> None:
    challenge_id = uuid4()

    challenge_repository.get_by_id.return_value = SimpleNamespace(
        id=challenge_id,
        is_active=True,
    )

    question_repository.get_by_position.return_value = SimpleNamespace(
        id=uuid4(),
        challenge_id=challenge_id,
        position=1,
    )

    request = QuestionCreateRequest(
        text="FastAPI supports async.",
        question_type=QuestionType.TRUE_FALSE,
        correct_answer="true",
        position=1,
    )

    with pytest.raises(ConflictError):
        await question_service.create_question(
            challenge_id,
            request,
        )

    question_repository.create.assert_not_awaited()
    session.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_create_question_rejects_missing_challenge(
    question_service: QuestionService,
    question_repository: AsyncMock,
    challenge_repository: AsyncMock,
) -> None:
    challenge_id = uuid4()

    challenge_repository.get_by_id.return_value = None

    request = QuestionCreateRequest(
        text="FastAPI supports async.",
        question_type=QuestionType.TRUE_FALSE,
        correct_answer="true",
        position=1,
    )

    with pytest.raises(ResourceNotFoundError):
        await question_service.create_question(
            challenge_id,
            request,
        )

    question_repository.create.assert_not_awaited()


@pytest.mark.asyncio
async def test_public_question_list_does_not_include_answers(
    question_service: QuestionService,
    question_repository: AsyncMock,
    challenge_repository: AsyncMock,
) -> None:
    challenge_id = uuid4()
    question_id = uuid4()

    challenge_repository.get_by_id.return_value = SimpleNamespace(
        id=challenge_id,
        status=ChallengeStatus.PUBLISHED,
        is_active=True,
    )

    question_repository.list_by_challenge.return_value = [
        SimpleNamespace(
            id=question_id,
            challenge_id=challenge_id,
            text="FastAPI supports async.",
            question_type=QuestionType.TRUE_FALSE,
            options=None,
            correct_answer="true",
            explanation="FastAPI supports async endpoints.",
            position=1,
            points=1,
            is_active=True,
        )
    ]

    question_repository.count_by_challenge.return_value = 1

    result = await question_service.list_public_questions(challenge_id)

    assert result.total == 1
    assert len(result.items) == 1

    serialized = result.items[0].model_dump()

    assert "correct_answer" not in serialized
    assert "explanation" not in serialized


@pytest.mark.asyncio
async def test_managed_question_list_includes_answers(
    question_service: QuestionService,
    question_repository: AsyncMock,
    challenge_repository: AsyncMock,
) -> None:
    challenge_id = uuid4()
    question_id = uuid4()
    now = datetime.now(UTC)

    challenge_repository.get_by_id.return_value = SimpleNamespace(
        id=challenge_id,
        status=ChallengeStatus.DRAFT,
        is_active=True,
    )

    question_repository.list_by_challenge.return_value = [
        SimpleNamespace(
            id=question_id,
            challenge_id=challenge_id,
            text="FastAPI supports async.",
            question_type=QuestionType.TRUE_FALSE,
            options=None,
            correct_answer="true",
            explanation="FastAPI supports async endpoints.",
            position=1,
            points=1,
            is_active=True,
            created_at=now,
            updated_at=now,
        )
    ]

    question_repository.count_by_challenge.return_value = 1

    result = await question_service.list_managed_questions(challenge_id)

    assert result.total == 1
    assert result.items[0].correct_answer == "true"
    assert result.items[0].explanation == "FastAPI supports async endpoints."


@pytest.mark.asyncio
async def test_update_question_rejects_duplicate_position(
    question_service: QuestionService,
    session: AsyncMock,
    question_repository: AsyncMock,
) -> None:
    challenge_id = uuid4()
    question_id = uuid4()

    question = SimpleNamespace(
        id=question_id,
        challenge_id=challenge_id,
        question_type=QuestionType.TRUE_FALSE,
        options=None,
        correct_answer="true",
        position=1,
        is_active=True,
    )

    conflicting_question = SimpleNamespace(
        id=uuid4(),
        challenge_id=challenge_id,
        position=2,
    )

    question_repository.get_by_id.return_value = question
    question_repository.get_by_position.return_value = conflicting_question

    request = QuestionUpdateRequest(
        position=2,
    )

    with pytest.raises(ConflictError):
        await question_service.update_question(
            question_id,
            request,
        )

    question_repository.update.assert_not_awaited()
    session.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_update_true_false_rejects_invalid_answer(
    question_service: QuestionService,
    session: AsyncMock,
    question_repository: AsyncMock,
) -> None:
    question_id = uuid4()

    question = SimpleNamespace(
        id=question_id,
        challenge_id=uuid4(),
        question_type=QuestionType.TRUE_FALSE,
        options=None,
        correct_answer="true",
        position=1,
        is_active=True,
    )

    question_repository.get_by_id.return_value = question

    request = QuestionUpdateRequest(
        correct_answer="yes",
    )

    with pytest.raises(ConflictError):
        await question_service.update_question(
            question_id,
            request,
        )

    question_repository.update.assert_not_awaited()
    session.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_update_multiple_choice_rejects_unknown_answer(
    question_service: QuestionService,
    session: AsyncMock,
    question_repository: AsyncMock,
) -> None:
    question_id = uuid4()

    question = SimpleNamespace(
        id=question_id,
        challenge_id=uuid4(),
        question_type=QuestionType.MULTIPLE_CHOICE,
        options=[
            {
                "key": "a",
                "text": "Python",
            },
            {
                "key": "b",
                "text": "Java",
            },
        ],
        correct_answer="a",
        position=1,
        is_active=True,
    )

    question_repository.get_by_id.return_value = question

    request = QuestionUpdateRequest(
        correct_answer="c",
    )

    with pytest.raises(ConflictError):
        await question_service.update_question(
            question_id,
            request,
        )

    question_repository.update.assert_not_awaited()
    session.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_delete_question_soft_deletes_question(
    question_service: QuestionService,
    session: AsyncMock,
    question_repository: AsyncMock,
) -> None:
    question_id = uuid4()

    question = SimpleNamespace(
        id=question_id,
        is_active=True,
    )

    question_repository.get_by_id.return_value = question
    question_repository.soft_delete.return_value = question

    await question_service.delete_question(question_id)

    question_repository.soft_delete.assert_awaited_once_with(question)

    session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_inactive_question_is_idempotent(
    question_service: QuestionService,
    session: AsyncMock,
    question_repository: AsyncMock,
) -> None:
    question_id = uuid4()

    question = SimpleNamespace(
        id=question_id,
        is_active=False,
    )

    question_repository.get_by_id.return_value = question

    await question_service.delete_question(question_id)

    question_repository.soft_delete.assert_not_awaited()
    session.commit.assert_not_awaited()
