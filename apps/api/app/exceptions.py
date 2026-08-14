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
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "details": exc.details,
                }
            },
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_error_handler(request: Request, exc: StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"code": "HTTP_ERROR", "message": exc.detail}},
        )

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        """Catch DB-level value errors (e.g. null bytes, integer overflow)."""
        msg = str(exc)
        if "null" in msg.lower() or "overflow" in msg.lower() or "out of range" in msg.lower():
            return JSONResponse(
                status_code=422,
                content={
                    "error": {
                        "code": "INVALID_VALUE",
                        "message": "Request contains invalid characters or values",
                    }
                },
            )
        # Re-raise others to the generic handler
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
            content={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred",
                }
            },
        )
