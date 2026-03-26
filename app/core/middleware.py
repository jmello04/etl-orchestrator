"""HTTP middleware for structured request/response logging."""

import time
import uuid

from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class LoggingMiddleware(BaseHTTPMiddleware):
    """Log every incoming request and outgoing response with timing information.

    Attaches a short random request ID to each request for log correlation
    and adds ``X-Request-ID`` and ``X-Process-Time`` headers to responses.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        """Process a request, log it, and return the response.

        Args:
            request: The incoming Starlette request.
            call_next: Callable that invokes the next middleware or route handler.

        Returns:
            The HTTP response, enriched with timing and request ID headers.

        Raises:
            Exception: Any exception raised by downstream handlers is re-raised
                       after being logged.
        """
        request_id = str(uuid.uuid4())[:8]
        start = time.perf_counter()

        logger.info(f"[{request_id}] -> {request.method} {request.url.path}")

        try:
            response = await call_next(request)
            duration = (time.perf_counter() - start) * 1000
            logger.info(
                f"[{request_id}] <- {request.method} {request.url.path} "
                f"| status={response.status_code} | {duration:.1f}ms"
            )
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = f"{duration:.1f}ms"
            return response

        except Exception as exc:
            duration = (time.perf_counter() - start) * 1000
            logger.error(
                f"[{request_id}] error {request.method} {request.url.path} "
                f"| error={exc} | {duration:.1f}ms"
            )
            raise
