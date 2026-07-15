from typing import Any


class AppException(Exception):
    """Base exception for expected application errors."""

    def __init__(
        self,
        *,
        status_code: int,
        code: str,
        message: str,
        details: Any | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details
        self.headers = headers

        super().__init__(message)


class ResourceNotFoundError(AppException):
    def __init__(
        self,
        *,
        resource: str,
        resource_id: str | int | None = None,
    ) -> None:
        details: dict[str, str | int] = {
            "resource": resource,
        }

        if resource_id is not None:
            details["resource_id"] = resource_id

        super().__init__(
            status_code=404,
            code="RESOURCE_NOT_FOUND",
            message=f"{resource} was not found.",
            details=details,
        )


class ConflictError(AppException):
    def __init__(
        self,
        *,
        message: str,
        details: Any | None = None,
    ) -> None:
        super().__init__(
            status_code=409,
            code="RESOURCE_CONFLICT",
            message=message,
            details=details,
        )


class ForbiddenError(AppException):
    def __init__(
        self,
        message: str = "You do not have permission to perform this action.",
    ) -> None:
        super().__init__(
            status_code=403,
            code="FORBIDDEN",
            message=message,
        )


class UnauthorizedError(AppException):
    def __init__(
        self,
        message: str = "Authentication is required.",
    ) -> None:
        super().__init__(
            status_code=401,
            code="UNAUTHORIZED",
            message=message,
            headers={"WWW-Authenticate": "Bearer"},
        )
