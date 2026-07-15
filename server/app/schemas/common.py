from typing import Any

from pydantic import BaseModel, Field


class ErrorDetails(BaseModel):
    code: str = Field(
        description="Machine-readable error code.",
        examples=["RESOURCE_NOT_FOUND"],
    )
    message: str = Field(
        description="Human-readable error message.",
        examples=["The requested resource was not found."],
    )
    details: Any | None = Field(
        default=None,
        description="Additional information about the error.",
    )


class ErrorResponse(BaseModel):
    error: ErrorDetails
    request_id: str | None = Field(
        default=None,
        description="Unique identifier assigned to the request.",
    )
