"""API Consumer Request Error Classifier — classify errors by root cause."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class ErrorClassification:
    error_id: str
    status_code: int
    root_cause: str  # "client_error", "auth_failure", "rate_limited", "server_error", "timeout", "validation"
    endpoint: str
    consumer_id: str

ROOT_CAUSES = {
    range(400, 401): "client_error",
    range(401, 404): "auth_failure",
    range(404, 405): "not_found",
    range(422, 423): "validation",
    range(429, 430): "rate_limited",
    range(500, 504): "server_error",
    range(504, 505): "timeout",
}

def classify(code: int) -> str:
    for r, cause in ROOT_CAUSES.items():
        if code in r: return cause
    return "server_error" if code >= 500 else "client_error"

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRequestErrorClassifier:
    def __init__(self) -> None:
        self._errors: dict[str, list[ErrorClassification]] = {}

    def record(self, installation_id: str, error_id: str, status_code: int, endpoint: str, consumer_id: str) -> ErrorClassification:
        if not installation_id: raise ValueError("installation_id is required")
        root = classify(status_code)
        ec = ErrorClassification(error_id=error_id, status_code=status_code, root_cause=root, endpoint=endpoint, consumer_id=consumer_id)
        self._errors.setdefault(installation_id, []).append(ec)
        return ec

    def by_root_cause(self, installation_id: str) -> dict[str, int]:
        counts: dict[str, int] = {}
        for e in self._errors.get(installation_id, []):
            counts[e.root_cause] = counts.get(e.root_cause, 0) + 1
        return counts

    def top_error_endpoints(self, installation_id: str, limit: int = 5) -> list[tuple[str, int]]:
        ep_counts: dict[str, int] = {}
        for e in self._errors.get(installation_id, []):
            ep_counts[e.endpoint] = ep_counts.get(e.endpoint, 0) + 1
        return sorted(ep_counts.items(), key=lambda x: -x[1])[:limit]

    def error_count(self, installation_id: str) -> int:
        return len(self._errors.get(installation_id, []))
