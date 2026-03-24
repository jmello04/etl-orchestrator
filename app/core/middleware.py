import time
import uuid
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = str(uuid.uuid4())[:8]
        inicio = time.perf_counter()

        logger.info(
            f"[{request_id}] → {request.method} {request.url.path}"
        )

        try:
            response = await call_next(request)
            duracao = (time.perf_counter() - inicio) * 1000
            logger.info(
                f"[{request_id}] ← {request.method} {request.url.path} "
                f"| status={response.status_code} | {duracao:.1f}ms"
            )
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = f"{duracao:.1f}ms"
            return response

        except Exception as exc:
            duracao = (time.perf_counter() - inicio) * 1000
            logger.error(
                f"[{request_id}] ✗ {request.method} {request.url.path} "
                f"| erro={exc} | {duracao:.1f}ms"
            )
            raise
