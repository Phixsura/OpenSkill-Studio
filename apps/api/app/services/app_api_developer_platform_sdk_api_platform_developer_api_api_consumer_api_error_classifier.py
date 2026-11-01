"""API Consumer Error Classifier — classify and categorize API errors."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class ErrorCategory:
    category: str  # "client", "server", "auth", "rate_limit", "validation", "timeout"
    count: int = 0
    latest_message: str = ""

@dataclass
class ClassifiedError:
    error_id: str
    status_code: int
    category: str
    message: str = ""
    endpoint: str = ""
    consumer_id: str = ""

ERROR_CATEGORIES = {
    range(400, 401): "client",
    range(401, 404): "auth",
    range(404, 405): "not_found",
    range(405, 413): "client",
    range(422, 423): "validation",
    range(429, 430): "rate_limit",
    range(500, 504): "server",
    range(504, 505): "timeout",
}

def classify_status(code: int) -> str:
    for r, cat in ERROR_CATEGORIES.items():
        if code in r: return cat
    if 400 <= code < 500: return "client"
    if code >= 500: return "server"
    return "unknown"

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiErrorClassifier:
    def __init__(self) -> None:
        self._errors: dict[str, list[ClassifiedError]] = {}
        self._categories: dict[tuple[str, str], ErrorCategory] = {}

    def classify(self, installation_id: str, error_id: str, status_code: int, message: str = "", endpoint: str = "", consumer_id: str = "") -> ClassifiedError:
        if not installation_id: raise ValueError("installation_id is required")
        cat = classify_status(status_code)
        err = ClassifiedError(error_id=error_id, status_code=status_code, category=cat, message=message, endpoint=endpoint, consumer_id=consumer_id)
        self._errors.setdefault(installation_id, []).append(err)
        ckey = (installation_id, cat)
        ec = self._categories.get(ckey)
        if ec is None: ec = ErrorCategory(category=cat); self._categories[ckey] = ec
        ec.count += 1
        ec.latest_message = message
        return err

    def by_category(self, installation_id: str) -> dict[str, int]:
        return {cat: ec.count for (inst, cat), ec in self._categories.items() if inst == installation_id}

    def top_errors(self, installation_id: str, limit: int = 10) -> list[ClassifiedError]:
        return list(reversed(self._errors.get(installation_id, [])[-limit:]))

    def error_count(self, installation_id: str) -> int:
        return len(self._errors.get(installation_id, []))
