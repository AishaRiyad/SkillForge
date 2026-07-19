from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.question import Question


class QuestionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        *,
        challenge_id: UUID,
        text: str,
        question_type: Any,
        options: list[dict[str, Any]] | None,
        correct_answer: str,
        explanation: str | None,
        position: int,
        points: int,
    ) -> Question:
        question = Question(
            challenge_id=challenge_id,
            text=text,
            question_type=question_type,
            options=options,
            correct_answer=correct_answer,
            explanation=explanation,
            position=position,
            points=points,
            is_active=True,
        )

        self.session.add(question)
        await self.session.flush()

        return question

    async def get_by_id(
        self,
        question_id: UUID,
        *,
        include_inactive: bool = False,
    ) -> Question | None:
        statement = select(Question).where(Question.id == question_id)

        if not include_inactive:
            statement = statement.where(Question.is_active.is_(True))

        result = await self.session.execute(statement)

        return result.scalar_one_or_none()

    async def get_by_position(
        self,
        *,
        challenge_id: UUID,
        position: int,
    ) -> Question | None:
        statement = select(Question).where(
            Question.challenge_id == challenge_id,
            Question.position == position,
        )

        result = await self.session.execute(statement)

        return result.scalar_one_or_none()

    async def list_by_challenge(
        self,
        challenge_id: UUID,
        *,
        include_inactive: bool = False,
    ) -> list[Question]:
        statement = select(Question).where(Question.challenge_id == challenge_id)

        if not include_inactive:
            statement = statement.where(Question.is_active.is_(True))

        statement = statement.order_by(Question.position.asc())

        result = await self.session.execute(statement)

        return list(result.scalars().all())

    async def count_by_challenge(
        self,
        challenge_id: UUID,
        *,
        include_inactive: bool = False,
    ) -> int:
        statement = select(func.count(Question.id)).where(
            Question.challenge_id == challenge_id
        )

        if not include_inactive:
            statement = statement.where(Question.is_active.is_(True))

        result = await self.session.execute(statement)

        return int(result.scalar_one())

    async def update(
        self,
        question: Question,
        update_data: dict[str, Any],
    ) -> Question:
        for field_name, value in update_data.items():
            setattr(question, field_name, value)

        await self.session.flush()

        return question

    async def soft_delete(
        self,
        question: Question,
    ) -> Question:
        question.is_active = False

        await self.session.flush()

        return question
