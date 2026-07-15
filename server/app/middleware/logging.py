import logging
from collections.abc import Awaitable, Callable
from time import perf_counter

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("skillforge.request")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        started_at = perf_counter()

        try:
            response = await call_next(request)
        except Exception:
            process_time_ms = (perf_counter() - started_at) * 1000

            logger.exception(
                "Request failed",
                extra={
                    "request_id": getattr(
                        request.state,
                        "request_id",
                        None,
                    ),
                    "method": request.method,
                    "path": request.url.path,
                    "process_time_ms": round(process_time_ms, 3),
                },
            )

            raise

        process_time_ms = (perf_counter() - started_at) * 1000

        logger.info(
            "Request completed",
            extra={
                "request_id": getattr(
                    request.state,
                    "request_id",
                    None,
                ),
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "process_time_ms": round(process_time_ms, 3),
            },
        )

        return response
