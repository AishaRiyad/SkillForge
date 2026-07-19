import pytest
from pydantic import ValidationError

from app.models.enums import ChallengeStatus
from app.schemas.challenge import (
    ChallengeCreateRequest,
    ChallengeUpdateRequest,
)


def test_challenge_create_normalizes_fields() -> None:
    request = ChallengeCreateRequest(
        title="  FastAPI   Basics Quiz  ",
        description="  Test your FastAPI knowledge.  ",
    )

    assert request.title == "FastAPI Basics Quiz"
    assert request.description == "Test your FastAPI knowledge."
    assert request.passing_score == 70
    assert request.xp_reward == 100
    assert request.status == ChallengeStatus.DRAFT


def test_challenge_create_converts_empty_description_to_none() -> None:
    request = ChallengeCreateRequest(
        title="FastAPI Quiz",
        description="   ",
    )

    assert request.description is None


def test_challenge_rejects_invalid_passing_score() -> None:
    with pytest.raises(ValidationError):
        ChallengeCreateRequest(
            title="FastAPI Quiz",
            passing_score=101,
        )


def test_challenge_rejects_negative_xp_reward() -> None:
    with pytest.raises(ValidationError):
        ChallengeCreateRequest(
            title="FastAPI Quiz",
            xp_reward=-1,
        )


def test_challenge_rejects_zero_max_attempts() -> None:
    with pytest.raises(ValidationError):
        ChallengeCreateRequest(
            title="FastAPI Quiz",
            max_attempts=0,
        )


def test_challenge_update_is_partial() -> None:
    request = ChallengeUpdateRequest(
        passing_score=80,
    )

    assert request.model_dump(exclude_unset=True) == {
        "passing_score": 80,
    }
