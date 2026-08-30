import structlog
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import DBAPIError
from starlette.exceptions import HTTPException as StarletteHTTPException

log = structlog.get_logger()

# Postgres SQLSTATEs produced by client-controllable INPUT (not server faults):
# a NUL/control char in a text/JSONB write, or a NaN/Infinity float. asyncpg
# raises these as CharacterNotInRepertoireError / UntranslatableCharacterError /
# InvalidTextRepresentation, wrapped by SQLAlchemy in DBAPIError — which is a
# SQLAlchemyError, NOT a ValueError, so the ValueError handler never caught them
# and every such request 500'd (R73/R86/R87/R88 kept finding these per-endpoint).
# This is the single global backstop: map them to a clean 422 regardless of which
# endpoint/column produced them. Per-schema screens remain (defense in depth +
# better field-level messages), but no unscreened surface can 500 on bad input.
_INPUT_SQLSTATES = frozenset(
    {
        "22021",  # character_not_in_repertoire (NUL byte in UTF-8)
        "22P05",  # untranslatable_character ( escape materialized)
        "22P02",  # invalid_text_representation (NaN/Infinity in JSONB)
    }
)


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

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError):
        """Format FastAPI's per-field validation errors into the app's error envelope."""
        details = []
        for err in exc.errors():
            field = ".".join(str(loc) for loc in err.get("loc", []) if loc != "body")
            details.append({"field": field, "message": err.get("msg", "Validation error")})
        message = details[0]["message"] if len(details) == 1 else f"{len(details)} validation errors"
        return JSONResponse(
            status_code=422,
            content=_error_body("VALIDATION_ERROR", message, request, details),
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

    @app.exception_handler(DBAPIError)
    async def dbapi_error_handler(request: Request, exc: DBAPIError):
        """Global backstop for input-driven Postgres write failures (R88).
        A NUL/control char or NaN/Infinity in any text/JSONB column raises an
        asyncpg error wrapped in DBAPIError (a SQLAlchemyError, not ValueError),
        which every per-endpoint screen kept missing → 500. Map the known
        input-fault SQLSTATEs to a clean 422; anything else is a genuine server
        fault and re-raises to the 500 handler."""
        sqlstate = getattr(getattr(exc, "orig", None), "sqlstate", None)
        if sqlstate in _INPUT_SQLSTATES:
            log.warning(
                "db_input_rejected",
                sqlstate=sqlstate,
                request_id=getattr(request.state, "request_id", None),
            )
            return JSONResponse(
                status_code=422,
                content=_error_body(
                    "INVALID_VALUE",
                    "Request contains invalid characters or values",
                    request,
                ),
            )
        raise exc

    @app.exception_handler(Exception)
    async def unhandled_error_handler(request: Request, exc: Exception):
        log.error(
            "unhandled_exception",
            error=str(exc),
            type=type(exc).__name__,
            request_id=getattr(request.state, "request_id", None),
            exc_info=True,
        )
        return JSONResponse(
            status_code=500,
            content=_error_body("INTERNAL_ERROR", "An unexpected error occurred", request),
        )
