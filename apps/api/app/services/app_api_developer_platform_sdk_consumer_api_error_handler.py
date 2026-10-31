"""Consumer API Error Handler — centralized error handling with retry policies."""
from __future__ import annotations

import structlog
from dataclasses import dataclass, field

logger = structlog.get_logger()


@dataclass
class ErrorPolicy:
    error_code: str
    retryable: bool = False
    max_retries: int = 3
    backoff_ms: int = 1000
    fallback_response: dict | None = None
    alert_on_count: int = 0  # alert after N occurrences, 0 = no alert


@dataclass
class ErrorOccurrence:
    error_code: str
    endpoint_id: str
    message: str
    timestamp: str = ""
    consumer_id: str = ""
    request_id: str = ""


@dataclass
class ErrorHandler:
    """Centralized error handling with policies and retry logic."""

    _policies: dict[str, ErrorPolicy] = field(default_factory=dict)
    _occurrences: list[ErrorOccurrence] = field(default_factory=list)
    _counts: dict[str, int] = field(default_factory=dict)
    _alerts: list[dict] = field(default_factory=list)

    def set_policy(self, policy: ErrorPolicy) -> dict:
        if policy.max_retries < 0:
            raise ValueError("max_retries must be non-negative")
        self._policies[policy.error_code] = policy
        logger.info("error_policy_set", error_code=policy.error_code)
        return {"error_code": policy.error_code, "retryable": policy.retryable}

    def handle(self, occurrence: ErrorOccurrence) -> dict:
        self._occurrences.append(occurrence)
        self._counts[occurrence.error_code] = self._counts.get(occurrence.error_code, 0) + 1
        count = self._counts[occurrence.error_code]

        policy = self._policies.get(occurrence.error_code)
        result: dict = {
            "error_code": occurrence.error_code,
            "occurrence_count": count,
        }

        if policy:
            result["retryable"] = policy.retryable
            if policy.retryable:
                result["max_retries"] = policy.max_retries
                result["backoff_ms"] = policy.backoff_ms
            if policy.fallback_response:
                result["fallback"] = policy.fallback_response
            if policy.alert_on_count > 0 and count >= policy.alert_on_count:
                alert = {"error_code": occurrence.error_code, "count": count,
                         "endpoint_id": occurrence.endpoint_id}
                self._alerts.append(alert)
                result["alert_triggered"] = True
        else:
            result["retryable"] = False
            result["policy"] = "default"

        return result

    def get_error_summary(self) -> dict:
        by_code: dict[str, int] = {}
        by_endpoint: dict[str, int] = {}
        for occ in self._occurrences:
            by_code[occ.error_code] = by_code.get(occ.error_code, 0) + 1
            by_endpoint[occ.endpoint_id] = by_endpoint.get(occ.endpoint_id, 0) + 1
        top_errors = sorted(by_code.items(), key=lambda x: x[1], reverse=True)[:5]
        top_endpoints = sorted(by_endpoint.items(), key=lambda x: x[1], reverse=True)[:5]
        return {
            "total_errors": len(self._occurrences),
            "unique_codes": len(by_code),
            "top_errors": [{"code": c, "count": n} for c, n in top_errors],
            "top_endpoints": [{"endpoint": e, "count": n} for e, n in top_endpoints],
            "alerts_triggered": len(self._alerts),
        }

    def get_alerts(self, limit: int = 20) -> list[dict]:
        return self._alerts[-limit:]

    def get_policy(self, error_code: str) -> dict | None:
        p = self._policies.get(error_code)
        if not p:
            return None
        return {"error_code": p.error_code, "retryable": p.retryable,
                "max_retries": p.max_retries, "backoff_ms": p.backoff_ms,
                "has_fallback": p.fallback_response is not None}

    def list_policies(self) -> list[dict]:
        return [self.get_policy(c) for c in sorted(self._policies)]

    def clear_counts(self) -> dict:
        count = len(self._counts)
        self._counts.clear()
        return {"cleared": count}
