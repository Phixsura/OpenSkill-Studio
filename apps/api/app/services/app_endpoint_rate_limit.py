"""Per-endpoint rate limiting for app API calls."""

from collections import defaultdict
from datetime import UTC, datetime

_counters: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))


def record_endpoint_call(app_id: str, endpoint: str) -> None:
    key = datetime.now(UTC).strftime("%Y-%m-%dT%H")
    _counters[f"{app_id}:{key}"][endpoint] += 1


def get_endpoint_usage(app_id: str) -> dict[str, int]:
    key = datetime.now(UTC).strftime("%Y-%m-%dT%H")
    return dict(_counters.get(f"{app_id}:{key}", {}))


def check_endpoint_limit(app_id: str, endpoint: str, *, limit: int = 100) -> bool:
    usage = get_endpoint_usage(app_id)
    return usage.get(endpoint, 0) < limit
