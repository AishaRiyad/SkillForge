from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from app.models.enums import QuestionType


class QuestionOption(BaseModel):
    key: str = Field(
        min_length=1,
        max_length=20,
    )

    text: str = Field(
        min_length=1,
        max_length=500,
    )

    @field_validator("key", "text")
    @classmethod
    def normalize_value(cls, value: str) -> str:
        return value.strip()


class QuestionCreateRequest(BaseModel):
    text: str = Field(
        min_length=3,
        max_length=5_000,
    )

    question_type: QuestionType

    options: list[QuestionOption] | None = None

    correct_answer: str = Field(
        min_length=1,
        max_length=500,
    )

    explanation: str | None = None

    position: int = Field(
        ge=1,
    )

    points: int = Field(
        default=1,
        ge=1,
        le=1_000,
    )

    @field_validator("text", "correct_answer")
    @classmethod
    def normalize_required_text(cls, value: str) -> str:
        normalized = value.strip()

        if not normalized:
            raise ValueError("Value cannot be empty.")

        return normalized

    @field_validator("explanation")
    @classmethod
    def normalize_optional_text(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        normalized = value.strip()

        return normalized or None

    @model_validator(mode="after")
    def validate_question_configuration(
        self,
    ) -> "QuestionCreateRequest":
        if self.question_type == QuestionType.MULTIPLE_CHOICE:
            if self.options is None or len(self.options) < 2:
                raise ValueError(
                    "Multiple-choice questions require at least two options."
                )

            option_keys = [option.key.lower() for option in self.options]

            if len(option_keys) != len(set(option_keys)):
                raise ValueError("Question option keys must be unique.")

            if self.correct_answer.lower() not in option_keys:
                raise ValueError("Correct answer must match an option key.")

        if self.question_type == QuestionType.TRUE_FALSE:
            normalized_answer = self.correct_answer.lower()

            if normalized_answer not in {"true", "false"}:
                raise ValueError("True/false answer must be true or false.")

            if self.options:
                raise ValueError("True/false questions must not contain options.")

            self.correct_answer = normalized_answer

        return self


class QuestionUpdateRequest(BaseModel):
    text: str | None = Field(
        default=None,
        min_length=3,
        max_length=5_000,
    )

    question_type: QuestionType | None = None

    options: list[QuestionOption] | None = None

    correct_answer: str | None = Field(
        default=None,
        min_length=1,
        max_length=500,
    )

    explanation: str | None = None

    position: int | None = Field(
        default=None,
        ge=1,
    )

    points: int | None = Field(
        default=None,
        ge=1,
        le=1_000,
    )

    is_active: bool | None = None


class PublicQuestionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    challenge_id: UUID
    text: str
    question_type: QuestionType
    options: list[dict[str, Any]] | None
    position: int
    points: int


class ManagedQuestionResponse(PublicQuestionResponse):
    correct_answer: str
    explanation: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class PublicQuestionListResponse(BaseModel):
    items: list[PublicQuestionResponse]
    total: int


class ManagedQuestionListResponse(BaseModel):
    items: list[ManagedQuestionResponse]
    total: int
