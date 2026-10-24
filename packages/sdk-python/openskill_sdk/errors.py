from __future__ import annotations

"""Error types for the OpenSkill SDK."""


class OpenSkillError(Exception):
    """Base error for all SDK errors."""

    def __init__(self, message: str, code: str = "UNKNOWN", status_code: int = 500):
        super().__init__(message)
        self.code = code
        self.status_code = status_code


class ApiError(OpenSkillError):
    """API returned an error response."""

    def __init__(self, message: str, code: str, status_code: int, details: list | None = None):
        super().__init__(message, code, status_code)
        self.details = details


class AuthError(OpenSkillError):
    """Authentication failed."""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, "AUTH_ERROR", 401)


class NotFoundError(OpenSkillError):
    """Resource not found."""

    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, "NOT_FOUND", 404)


class RateLimitError(OpenSkillError):
    """Rate limit exceeded."""

    def __init__(self, retry_after: int = 60, message: str = "Rate limit exceeded"):
        super().__init__(message, "RATE_LIMITED", 429)
        self.retry_after = retry_after


class ValidationError(OpenSkillError):
    """Validation failed."""

    def __init__(self, message: str, details: list | None = None):
        super().__init__(message, "VALIDATION_ERROR", 422)
        self.details = details
