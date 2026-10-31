"""App API Developer Webhook Error Classifier — classify webhook delivery errors."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class ErrorClass:
    error_class: str  # "timeout", "connection_refused", "dns_failure", "tls_error", "http_4xx", "http_5xx", "payload_rejected"
    count: int = 0
    destinations_affected: set[str] = field(default_factory=set)

class AppAPIDeveloperPlatformSDKApiDeveloperApiWebhookErrorClassifier:
    def __init__(self) -> None:
        self._classes: dict[tuple[str, str], ErrorClass] = {}

    def classify(self, installation_id: str, error_class: str, destination: str) -> ErrorClass:
        if not installation_id: raise ValueError("installation_id is required")
        valid = {"timeout", "connection_refused", "dns_failure", "tls_error", "http_4xx", "http_5xx", "payload_rejected"}
        if error_class not in valid: raise ValueError(f"Invalid error class: {error_class}")
        key = (installation_id, error_class)
        if key not in self._classes:
            self._classes[key] = ErrorClass(error_class=error_class)
        c = self._classes[key]
        c.count += 1
        c.destinations_affected.add(destination)
        return c

    def top_errors(self, installation_id: str) -> list[ErrorClass]:
        classes = [c for (inst, _), c in self._classes.items() if inst == installation_id]
        return sorted(classes, key=lambda c: c.count, reverse=True)

    def by_class(self, installation_id: str, error_class: str) -> ErrorClass | None:
        return self._classes.get((installation_id, error_class))

    def total_errors(self, installation_id: str) -> int:
        return sum(c.count for (inst, _), c in self._classes.items() if inst == installation_id)
