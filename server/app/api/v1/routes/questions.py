from uuid import UUID

from fastapi import APIRouter, Response, status

from app.api.dependencies import (
    AdminUser,
    QuestionServiceDependency,
)
from app.schemas.question import (
    ManagedQuestionListResponse,
    ManagedQuestionResponse,
    PublicQuestionListResponse,
    QuestionCreateRequest,
    QuestionUpdateRequest,
)

router = APIRouter(
    tags=["Questions"],
)


@router.get(
    "/challenges/{challenge_id}/questions",
    response_model=PublicQuestionListResponse,
)
async def list_public_questions(
    challenge_id: UUID,
    question_service: QuestionServiceDependency,
) -> PublicQuestionListResponse:
    return await question_service.list_public_questions(challenge_id)


@router.get(
    "/admin/challenges/{challenge_id}/questions",
    response_model=ManagedQuestionListResponse,
)
async def list_managed_questions(
    challenge_id: UUID,
    current_admin: AdminUser,
    question_service: QuestionServiceDependency,
) -> ManagedQuestionListResponse:
    del current_admin

    return await question_service.list_managed_questions(challenge_id)


@router.post(
    "/challenges/{challenge_id}/questions",
    response_model=ManagedQuestionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_question(
    challenge_id: UUID,
    request: QuestionCreateRequest,
    current_admin: AdminUser,
    question_service: QuestionServiceDependency,
) -> ManagedQuestionResponse:
    del current_admin

    question = await question_service.create_question(
        challenge_id,
        request,
    )

    return ManagedQuestionResponse.model_validate(question)


@router.patch(
    "/questions/{question_id}",
    response_model=ManagedQuestionResponse,
)
async def update_question(
    question_id: UUID,
    request: QuestionUpdateRequest,
    current_admin: AdminUser,
    question_service: QuestionServiceDependency,
) -> ManagedQuestionResponse:
    del current_admin

    question = await question_service.update_question(
        question_id,
        request,
    )

    return ManagedQuestionResponse.model_validate(question)


@router.delete(
    "/questions/{question_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_question(
    question_id: UUID,
    current_admin: AdminUser,
    question_service: QuestionServiceDependency,
) -> Response:
    del current_admin

    await question_service.delete_question(question_id)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
