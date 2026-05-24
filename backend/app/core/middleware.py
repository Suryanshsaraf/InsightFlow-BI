"""
Middlewares and exception handlers for FastAPI.

Includes execution timing middleware and handlers for mapping exceptions
to structured JSON responses.
"""

import time
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from app.core.exceptions import BaseAppException
from app.core.logging import logger


class TimingMiddleware(BaseHTTPMiddleware):
    """Middleware that logs the request path, method, status, and duration."""
    
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        start_time = time.perf_counter()
        
        # Add context vars for structured logging
        structlog_keys = {
            "method": request.method,
            "path": request.url.path,
        }
        
        try:
            response = await call_next(request)
            duration = time.perf_counter() - start_time
            
            logger.info(
                "Request completed",
                status_code=response.status_code,
                duration_ms=round(duration * 1000, 2),
                **structlog_keys,
            )
            return response
        except Exception as exc:
            duration = time.perf_counter() - start_time
            logger.error(
                "Request failed",
                error=str(exc),
                duration_ms=round(duration * 1000, 2),
                **structlog_keys,
            )
            raise


async def app_exception_handler(request: Request, exc: BaseAppException) -> JSONResponse:
    """Handle custom application exceptions and format as JSON."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "data": None,
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
            },
        },
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Fallback handler for unhandled server exceptions."""
    logger.exception("Unhandled server error", path=request.url.path)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "data": None,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred.",
                "details": {},
            },
        },
    )
