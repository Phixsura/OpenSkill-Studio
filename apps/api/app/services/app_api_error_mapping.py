"""App API Error Mapping — map internal errors to public API errors.

Manages error mappings:
- Map internal error codes to public codes
- Define HTTP status and user messages
- Track error occurrence counts
- Per-installation scoped mappings
"""

from __future__ import annotations

from dataclasses import dataclass

import structlog

log = structlog.get_logger()


@dataclass
class ErrorMapping:
    """A mapping from internal to public error."""

    internal_code: str
    public_code: str
    http_status: int
    message: str
    occurrences: int = 0


class AppAPIErrorMapping:
    """Map internal errors to public API errors."""

    def __init__(self) -> None:
        self._mappings: dict[tuple[str, str], ErrorMapping] = {}

    def define(
        self, installation_id: str, internal_code: str,
        public_code: str, http_status: int, message: str,
    ) -> ErrorMapping:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not (400 <= http_status < 600):
            raise ValueError("http_status must be 4xx or 5xx")

        m = ErrorMapping(
            internal_code=internal_code, public_code=public_code,
            http_status=http_status, message=message,
        )
        self._mappings[(installation_id, internal_code)] = m
        return m

    def resolve(self, installation_id: str, internal_code: str) -> ErrorMapping | None:
        key = (installation_id, internal_code)
        m = self._mappings.get(key)
        if m:
            m.occurrences += 1
        return m

    def top_errors(self, installation_id: str, limit: int = 10) -> list[ErrorMapping]:
        mappings = [m for (inst, _), m in self._mappings.items() if inst == installation_id and m.occurrences > 0]
        return sorted(mappings, key=lambda m: m.occurrences, reverse=True)[:limit]

    def list_mappings(self, installation_id: str) -> list[ErrorMapping]:
        return [m for (inst, _), m in self._mappings.items() if inst == installation_id]
