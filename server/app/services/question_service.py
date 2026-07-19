from typing import Any
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    ConflictError,
    ResourceNotFoundError,
)
from app.models.enums import QuestionType
from app.models.question import Question
from app.repositories.challenge_repository import ChallengeRepository
from app.repositories.question_repository import QuestionRepository
from app.schemas.question import (
    ManagedQuestionListResponse,
    ManagedQuestionResponse,
    PublicQuestionListResponse,
    PublicQuestionResponse,
    QuestionCreateRequest,
    QuestionUpdateRequest,
)


class QuestionService:
    def __init__(
        self,
        session: AsyncSession,
        question_repository: QuestionRepository,
        challenge_repository: ChallengeRepository,
    ) -> None:
        self.session = session
        self.question_repository = question_repository
        self.challenge_repository = challenge_repository

    async def create_question(
        self,
        challenge_id: UUID,
        request: QuestionCreateRequest,
    ) -> Question:
        await self._ensure_challenge_exists(challenge_id)

        existing_position = await self.question_repository.get_by_position(
            challenge_id=challenge_id,
            position=request.position,
        )

        if existing_position is not None:
            raise ConflictError(
                message=(
                    "A question with this position already exists in the challenge."
                ),
                details={"field": "position"},
            )

        options: list[dict[str, Any]] | None = None

        if request.options is not None:
            options = [option.model_dump() for option in request.options]

        try:
            question = await self.question_repository.create(
                challenge_id=challenge_id,
                text=request.text,
                question_type=request.question_type,
                options=options,
                correct_answer=request.correct_answer.lower(),
                explanation=request.explanation,
                position=request.position,
                points=request.points,
            )

            await self.session.commit()
            await self.session.refresh(question)

            return question

        except IntegrityError as exception:
            await self.session.rollback()

            raise ConflictError(
                message=(
                    "A question with this position already exists in the challenge."
                ),
                details={"field": "position"},
            ) from exception

        except Exception:
            await self.session.rollback()
            raise

    async def get_managed_question(
        self,
        question_id: UUID,
    ) -> Question:
        question = await self.question_repository.get_by_id(
            question_id,
            include_inactive=True,
        )

        if question is None:
            raise ResourceNotFoundError(
                resource="Question",
                resource_id=str(question_id),
            )

        return question

    async def list_public_questions(
        self,
        challenge_id: UUID,
    ) -> PublicQuestionListResponse:
        await self._ensure_public_challenge_exists(challenge_id)

        questions = await self.question_repository.list_by_challenge(challenge_id)

        total = await self.question_repository.count_by_challenge(challenge_id)

        return PublicQuestionListResponse(
            items=[
                PublicQuestionResponse.model_validate(question)
                for question in questions
            ],
            total=total,
        )

    async def list_managed_questions(
        self,
        challenge_id: UUID,
    ) -> ManagedQuestionListResponse:
        await self._ensure_challenge_exists(challenge_id)

        questions = await self.question_repository.list_by_challenge(
            challenge_id,
            include_inactive=True,
        )

        total = await self.question_repository.count_by_challenge(
            challenge_id,
            include_inactive=True,
        )

        return ManagedQuestionListResponse(
            items=[
                ManagedQuestionResponse.model_validate(question)
                for question in questions
            ],
            total=total,
        )

    async def update_question(
        self,
        question_id: UUID,
        request: QuestionUpdateRequest,
    ) -> Question:
        question = await self.get_managed_question(question_id)

        update_data = request.model_dump(exclude_unset=True)

        if not update_data:
            return question

        requested_position = update_data.get("position")

        if requested_position is not None and requested_position != question.position:
            existing_position = await self.question_repository.get_by_position(
                challenge_id=question.challenge_id,
                position=requested_position,
            )

            if existing_position is not None and existing_position.id != question.id:
                raise ConflictError(
                    message=(
                        "A question with this position already exists in the challenge."
                    ),
                    details={"field": "position"},
                )

        if "options" in update_data:
            options = update_data["options"]

            if options is not None:
                update_data["options"] = [
                    (option.model_dump() if hasattr(option, "model_dump") else option)
                    for option in options
                ]

        self._validate_updated_configuration(
            question,
            update_data,
        )

        if "correct_answer" in update_data:
            answer = update_data["correct_answer"]

            if answer is not None:
                update_data["correct_answer"] = answer.lower()

        try:
            updated_question = await self.question_repository.update(
                question,
                update_data,
            )

            await self.session.commit()
            await self.session.refresh(updated_question)

            return updated_question

        except IntegrityError as exception:
            await self.session.rollback()

            raise ConflictError(
                message=(
                    "A question with this position already exists in the challenge."
                ),
                details={"field": "position"},
            ) from exception

        except Exception:
            await self.session.rollback()
            raise

    async def delete_question(
        self,
        question_id: UUID,
    ) -> None:
        question = await self.get_managed_question(question_id)

        if not question.is_active:
            return

        try:
            await self.question_repository.soft_delete(question)
            await self.session.commit()

        except Exception:
            await self.session.rollback()
            raise

    async def _ensure_challenge_exists(
        self,
        challenge_id: UUID,
    ) -> None:
        challenge = await self.challenge_repository.get_by_id(
            challenge_id,
            include_inactive=False,
            include_unpublished=True,
        )

        if challenge is None:
            raise ResourceNotFoundError(
                resource="Active challenge",
                resource_id=str(challenge_id),
            )

    async def _ensure_public_challenge_exists(
        self,
        challenge_id: UUID,
    ) -> None:
        challenge = await self.challenge_repository.get_by_id(challenge_id)

        if challenge is None:
            raise ResourceNotFoundError(
                resource="Published challenge",
                resource_id=str(challenge_id),
            )

    def _validate_updated_configuration(
        self,
        question: Question,
        update_data: dict[str, Any],
    ) -> None:
        question_type = update_data.get(
            "question_type",
            question.question_type,
        )

        options = update_data.get(
            "options",
            question.options,
        )

        correct_answer = update_data.get(
            "correct_answer",
            question.correct_answer,
        )

        normalized_answer = correct_answer.lower()

        if question_type == QuestionType.TRUE_FALSE:
            if normalized_answer not in {"true", "false"}:
                raise ConflictError(
                    message=("True/false answer must be true or false."),
                    details={"field": "correct_answer"},
                )

            if options:
                raise ConflictError(
                    message=("True/false questions must not contain options."),
                    details={"field": "options"},
                )

        if question_type == QuestionType.MULTIPLE_CHOICE:
            if options is None or len(options) < 2:
                raise ConflictError(
                    message=("Multiple-choice questions require at least two options."),
                    details={"field": "options"},
                )

            option_keys = [str(option["key"]).lower() for option in options]

            if normalized_answer not in option_keys:
                raise ConflictError(
                    message=("Correct answer must match an option key."),
                    details={"field": "correct_answer"},
                )
