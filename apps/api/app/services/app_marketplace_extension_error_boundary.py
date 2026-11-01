"""Error Boundary — centralized error handling for extension execution.

Catches, classifies, and reports errors from extension sandboxes with
automatic retry for transient failures, circuit breaking for persistent
errors, and structured error reports.
"""
from __future__ import annotations
import secrets
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class ErrorCategory(str, Enum):
    RUNTIME = "runtime"
    TIMEOUT = "timeout"
    MEMORY = "memory"
    NETWORK = "network"
    PERMISSION = "permission"
    VALIDATION = "validation"
    DEPENDENCY = "dependency"
    UNKNOWN = "unknown"


class ErrorAction(str, Enum):
    RETRY = "retry"
    SKIP = "skip"
    HALT = "halt"
    FALLBACK = "fallback"


TRANSIENT_CATEGORIES = {ErrorCategory.TIMEOUT, ErrorCategory.NETWORK}


@dataclass
class CaughtError:
    error_id: str
    extension_id: str
    category: ErrorCategory
    message: str
    stack_trace: str = ""
    action_taken: ErrorAction = ErrorAction.SKIP
    retry_count: int = 0
    resolved: bool = False
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


class ErrorBoundaryService:
    """Catches and handles extension errors with retry and circuit breaking."""

    MAX_RETRIES = 3
    CIRCUIT_THRESHOLD = 10  # errors before circuit opens

    def __init__(self):
        self._errors: list[CaughtError] = []
        self._error_counts: dict[str, int] = defaultdict(int)
        self._circuit_open: set[str] = set()
        self._fallbacks: dict[str, dict] = {}

    def register_fallback(self, extension_id: str, function_name: str,
                          fallback_response: dict) -> None:
        self._fallbacks[f"{extension_id}:{function_name}"] = fallback_response

    def handle_error(self, extension_id: str, message: str,
                     category: ErrorCategory = ErrorCategory.UNKNOWN,
                     stack_trace: str = "",
                     function_name: str = "") -> CaughtError:
        # Determine action
        if extension_id in self._circuit_open:
            action = ErrorAction.HALT
        elif category in TRANSIENT_CATEGORIES:
            action = ErrorAction.RETRY
        elif f"{extension_id}:{function_name}" in self._fallbacks:
            action = ErrorAction.FALLBACK
        else:
            action = ErrorAction.SKIP

        error = CaughtError(
            error_id=f"err_{secrets.token_urlsafe(8)}",
            extension_id=extension_id, category=category,
            message=message, stack_trace=stack_trace,
            action_taken=action,
        )
        self._errors.append(error)
        self._error_counts[extension_id] += 1

        # Check circuit breaker
        if self._error_counts[extension_id] >= self.CIRCUIT_THRESHOLD:
            self._circuit_open.add(extension_id)

        return error

    def is_circuit_open(self, extension_id: str) -> bool:
        return extension_id in self._circuit_open

    def reset_circuit(self, extension_id: str) -> bool:
        if extension_id in self._circuit_open:
            self._circuit_open.discard(extension_id)
            self._error_counts[extension_id] = 0
            return True
        return False

    def get_fallback(self, extension_id: str, function_name: str) -> dict | None:
        return self._fallbacks.get(f"{extension_id}:{function_name}")

    def get_errors(self, extension_id: str, category: ErrorCategory | None = None,
                   limit: int = 50) -> list[CaughtError]:
        errors = [e for e in self._errors if e.extension_id == extension_id]
        if category:
            errors = [e for e in errors if e.category == category]
        return errors[-limit:]

    def get_summary(self, extension_id: str) -> dict:
        errors = [e for e in self._errors if e.extension_id == extension_id]
        by_cat: dict[str, int] = defaultdict(int)
        for e in errors:
            by_cat[e.category.value] += 1
        return {
            "total": len(errors),
            "by_category": dict(by_cat),
            "circuit_open": self.is_circuit_open(extension_id),
            "error_rate": self._error_counts.get(extension_id, 0),
        }

    def resolve(self, error_id: str) -> bool:
        error = next((e for e in self._errors if e.error_id == error_id), None)
        if error:
            error.resolved = True
            return True
        return False
