import structlog
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

log = structlog.get_logger()


class AppError(Exception):
    """Application business error base class."""

    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 400,
        details: list | None = None,
    ):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details


def register_exception_handlers(app: FastAPI) -> None:
    def _error_body(code: str, message: str, request: Request, details: list | None = None) -> dict:
        """Stripe-style error response with request_id for debugging."""
        body: dict = {
            "error": {
                "code": code,
                "message": message,
                "request_id": getattr(request.state, "request_id", None),
            }
        }
        if details:
            body["error"]["details"] = details
        return body

    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError):
        log.warning(
            "app_error",
            code=exc.code,
            message=exc.message,
            request_id=getattr(request.state, "request_id", None),
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_body(exc.code, exc.message, request, exc.details),
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_error_handler(request: Request, exc: StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_body("HTTP_ERROR", exc.detail or "Request error", request),
        )

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        """Catch DB-level value errors (e.g. null bytes, integer overflow)."""
        msg = str(exc)
        if "null" in msg.lower() or "overflow" in msg.lower() or "out of range" in msg.lower():
            return JSONResponse(
                status_code=422,
                content=_error_body("INVALID_VALUE", "Request contains invalid characters or values", request),
            )
        raise exc

    @app.exception_handler(Exception)
    async def unhandled_error_handler(request: Request, exc: Exception):
        log.error(
            "unhandled_exception",
            error=str(exc),
            type=type(exc).__name__,
            request_id=getattr(request.state, "request_id", None),
        )
        return JSONResponse(
            status_code=500,
            content=_error_body("INTERNAL_ERROR", "An unexpected error occurred", request),
        )
