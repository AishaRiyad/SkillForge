import pytest
from pydantic import ValidationError

from app.models.enums import QuestionType
from app.schemas.question import (
    PublicQuestionResponse,
    QuestionCreateRequest,
)


def test_create_valid_multiple_choice_question() -> None:
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
        correct_answer="a",
        position=1,
        points=2,
    )

    assert request.question_type == QuestionType.MULTIPLE_CHOICE
    assert request.correct_answer == "a"
    assert request.options is not None
    assert len(request.options) == 2


def test_multiple_choice_requires_at_least_two_options() -> None:
    with pytest.raises(ValidationError):
        QuestionCreateRequest(
            text="Which language is used?",
            question_type=QuestionType.MULTIPLE_CHOICE,
            options=[
                {
                    "key": "a",
                    "text": "Python",
                },
            ],
            correct_answer="a",
            position=1,
        )


def test_multiple_choice_rejects_missing_options() -> None:
    with pytest.raises(ValidationError):
        QuestionCreateRequest(
            text="Which language is used?",
            question_type=QuestionType.MULTIPLE_CHOICE,
            options=None,
            correct_answer="a",
            position=1,
        )


def test_multiple_choice_rejects_duplicate_option_keys() -> None:
    with pytest.raises(ValidationError):
        QuestionCreateRequest(
            text="Which language is used?",
            question_type=QuestionType.MULTIPLE_CHOICE,
            options=[
                {
                    "key": "a",
                    "text": "Python",
                },
                {
                    "key": "A",
                    "text": "Java",
                },
            ],
            correct_answer="a",
            position=1,
        )


def test_multiple_choice_rejects_unknown_correct_answer() -> None:
    with pytest.raises(ValidationError):
        QuestionCreateRequest(
            text="Which language is used?",
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
            correct_answer="c",
            position=1,
        )


def test_create_valid_true_false_question() -> None:
    request = QuestionCreateRequest(
        text="FastAPI supports asynchronous endpoints.",
        question_type=QuestionType.TRUE_FALSE,
        options=None,
        correct_answer="TRUE",
        position=1,
    )

    assert request.correct_answer == "true"
    assert request.options is None


def test_true_false_rejects_invalid_answer() -> None:
    with pytest.raises(ValidationError):
        QuestionCreateRequest(
            text="FastAPI supports async.",
            question_type=QuestionType.TRUE_FALSE,
            options=None,
            correct_answer="yes",
            position=1,
        )


def test_true_false_rejects_options() -> None:
    with pytest.raises(ValidationError):
        QuestionCreateRequest(
            text="FastAPI supports async.",
            question_type=QuestionType.TRUE_FALSE,
            options=[
                {
                    "key": "true",
                    "text": "True",
                },
                {
                    "key": "false",
                    "text": "False",
                },
            ],
            correct_answer="true",
            position=1,
        )


def test_question_rejects_invalid_position() -> None:
    with pytest.raises(ValidationError):
        QuestionCreateRequest(
            text="FastAPI supports async.",
            question_type=QuestionType.TRUE_FALSE,
            correct_answer="true",
            position=0,
        )


def test_public_question_response_does_not_expose_answer() -> None:
    response_fields = PublicQuestionResponse.model_fields

    assert "correct_answer" not in response_fields
    assert "explanation" not in response_fields
