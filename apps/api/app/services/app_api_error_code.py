"""App API Error Code — manage standardized API error codes.

Manages error codes:
- Define error codes with messages and HTTP status
- Lookup error details by code
- Categorize errors
- Per-installation scoped codes
"""

from __future__ import annotations

from dataclasses import dataclass

import structlog

log = structlog.get_logger()


@dataclass
class ErrorCodeDef:
    """A standardized API error code."""

    code: str  # e.g., "AUTH_EXPIRED"
    message: str
    http_status: int
    category: str = "general"
    retryable: bool = False


class AppAPIErrorCode:
    """Manage standardized API error codes."""

    def __init__(self) -> None:
        self._codes: dict[tuple[str, str], ErrorCodeDef] = {}

    def define(
        self, installation_id: str, code: str, message: str,
        http_status: int, category: str = "general", retryable: bool = False,
    ) -> ErrorCodeDef:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not code:
            raise ValueError("code is required")
        if not (400 <= http_status < 600):
            raise ValueError("http_status must be 4xx or 5xx")

        key = (installation_id, code)
        if key in self._codes:
            raise ValueError(f"Error code {code} already defined")

        ec = ErrorCodeDef(
            code=code, message=message, http_status=http_status,
            category=category, retryable=retryable,
        )
        self._codes[key] = ec
        return ec

    def lookup(self, installation_id: str, code: str) -> ErrorCodeDef:
        key = (installation_id, code)
        ec = self._codes.get(key)
        if ec is None:
            raise KeyError(f"Error code {code} not found")
        return ec

    def by_category(self, installation_id: str, category: str) -> list[ErrorCodeDef]:
        return [ec for (inst, _), ec in self._codes.items() if inst == installation_id and ec.category == category]

    def list_codes(self, installation_id: str) -> list[ErrorCodeDef]:
        return sorted(
            [ec for (inst, _), ec in self._codes.items() if inst == installation_id],
            key=lambda e: e.code,
        )
