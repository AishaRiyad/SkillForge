import logging
from typing import Any

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from app.core.exceptions import AppException

logger = logging.getLogger(__name__)


def get_request_id(request: Request) -> str | None:
    return getattr(request.state, "request_id", None)


def create_error_content(
    *,
    request: Request,
    code: str,
    message: str,
    details: Any | None = None,
) -> dict[str, Any]:
    return {
        "error": {
            "code": code,
            "message": message,
            "details": details,
        },
        "request_id": get_request_id(request),
    }


async def app_exception_handler(
    request: Request,
    exception: AppException,
) -> JSONResponse:
    return JSONResponse(
        status_code=exception.status_code,
        content=create_error_content(
            request=request,
            code=exception.code,
            message=exception.message,
            details=exception.details,
        ),
        headers=exception.headers,
    )


async def validation_exception_handler(
    request: Request,
    exception: RequestValidationError,
) -> JSONResponse:
    validation_errors = jsonable_encoder(
        exception.errors(),
        custom_encoder={
            ValueError: str,
        },
    )

    return JSONResponse(
        status_code=422,
        content=create_error_content(
            request=request,
            code="VALIDATION_ERROR",
            message="The submitted data is invalid.",
            details=validation_errors,
        ),
    )


async def http_exception_handler(
    request: Request,
    exception: StarletteHTTPException,
) -> JSONResponse:
    message = (
        exception.detail
        if isinstance(exception.detail, str)
        else "The request could not be completed."
    )

    return JSONResponse(
        status_code=exception.status_code,
        content=create_error_content(
            request=request,
            code="HTTP_ERROR",
            message=message,
            details=None,
        ),
        headers=exception.headers,
    )


async def unexpected_exception_handler(
    request: Request,
    exception: Exception,
) -> JSONResponse:
    logger.exception(
        "Unhandled application exception",
        extra={
            "request_id": get_request_id(request),
            "path": request.url.path,
            "method": request.method,
        },
        exc_info=exception,
    )

    return JSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content=create_error_content(
            request=request,
            code="INTERNAL_SERVER_ERROR",
            message="An unexpected error occurred.",
        ),
    )


def register_exception_handlers(application: FastAPI) -> None:
    application.add_exception_handler(
        AppException,
        app_exception_handler,  # type: ignore[arg-type]
    )
    application.add_exception_handler(
        RequestValidationError,
        validation_exception_handler,  # type: ignore[arg-type]
    )
    application.add_exception_handler(
        StarletteHTTPException,
        http_exception_handler,  # type: ignore[arg-type]
    )
    application.add_exception_handler(
        Exception,
        unexpected_exception_handler,
    )
