import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.challenge import Challenge
from app.models.enums import (
    ChallengeStatus,
    QuestionType,
)
from app.models.lesson import Lesson
from app.repositories.question_repository import QuestionRepository


@pytest.mark.asyncio
async def test_create_and_get_question(
    db_session: AsyncSession,
    lesson: Lesson,
) -> None:
    challenge = Challenge(
        lesson_id=lesson.id,
        title="FastAPI Quiz",
        passing_score=70,
        xp_reward=100,
        status=ChallengeStatus.DRAFT,
        is_active=True,
    )

    db_session.add(challenge)
    await db_session.flush()

    repository = QuestionRepository(db_session)

    created = await repository.create(
        challenge_id=challenge.id,
        text="FastAPI supports async.",
        question_type=QuestionType.TRUE_FALSE,
        options=None,
        correct_answer="true",
        explanation=None,
        position=1,
        points=1,
    )

    found = await repository.get_by_id(created.id)

    assert found is not None
    assert found.id == created.id
    assert found.challenge_id == challenge.id
    assert found.correct_answer == "true"
    assert found.position == 1
