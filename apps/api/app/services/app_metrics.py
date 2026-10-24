"""App metrics aggregation — real-time counters and historical rollups.

Provides lightweight metrics collection for dashboards without
requiring a full time-series database.
"""

from collections import defaultdict
from datetime import UTC, datetime

import structlog

log = structlog.get_logger()

# In-memory metric counters (production: Redis sorted sets)
_COUNTERS: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))


def _day_key() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%d")


def increment(metric: str, app_id: str, amount: int = 1) -> None:
    """Increment a metric counter for an app."""
    key = f"{_day_key()}:{app_id}"
    _COUNTERS[metric][key] += amount


def get_count(metric: str, app_id: str) -> int:
    """Get today's count for a metric."""
    key = f"{_day_key()}:{app_id}"
    return _COUNTERS[metric].get(key, 0)


def get_all_counts(app_id: str) -> dict[str, int]:
    """Get all metric counts for today."""
    day = _day_key()
    key_suffix = f"{day}:{app_id}"
    return {
        metric: counts.get(key_suffix, 0)
        for metric, counts in _COUNTERS.items()
    }


# Predefined metrics
METRIC_API_CALLS = "api_calls"
METRIC_WEBHOOK_DELIVERIES = "webhook_deliveries"
METRIC_WEBHOOK_FAILURES = "webhook_failures"
METRIC_SANDBOX_EXECUTIONS = "sandbox_executions"
METRIC_SANDBOX_FAILURES = "sandbox_failures"
METRIC_EVENT_DISPATCHES = "event_dispatches"
METRIC_INSTALLS = "installs"
METRIC_UNINSTALLS = "uninstalls"


def record_api_call(app_id: str) -> None:
    increment(METRIC_API_CALLS, app_id)


def record_webhook_delivery(app_id: str, success: bool = True) -> None:
    increment(METRIC_WEBHOOK_DELIVERIES, app_id)
    if not success:
        increment(METRIC_WEBHOOK_FAILURES, app_id)


def record_sandbox_execution(app_id: str, success: bool = True) -> None:
    increment(METRIC_SANDBOX_EXECUTIONS, app_id)
    if not success:
        increment(METRIC_SANDBOX_FAILURES, app_id)


def record_event_dispatch(app_id: str) -> None:
    increment(METRIC_EVENT_DISPATCHES, app_id)


def record_install(app_id: str) -> None:
    increment(METRIC_INSTALLS, app_id)


def record_uninstall(app_id: str) -> None:
    increment(METRIC_UNINSTALLS, app_id)
