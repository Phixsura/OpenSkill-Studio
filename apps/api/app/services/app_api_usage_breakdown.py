"""App API Usage Breakdown — break down API usage by dimension.

Manages usage breakdowns:
- Track usage by endpoint, method, consumer
- Top-N queries per dimension
- Per-installation scoped breakdowns
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


class AppAPIUsageBreakdown:
    """Break down API usage by dimension."""

    def __init__(self) -> None:
        self._by_endpoint: dict[tuple[str, str], int] = {}
        self._by_consumer: dict[tuple[str, str], int] = {}
        self._by_method: dict[tuple[str, str], int] = {}

    def record(self, installation_id: str, endpoint: str, method: str, consumer: str) -> None:
        if not installation_id:
            raise ValueError("installation_id is required")
        self._by_endpoint[(installation_id, endpoint)] = self._by_endpoint.get((installation_id, endpoint), 0) + 1
        self._by_consumer[(installation_id, consumer)] = self._by_consumer.get((installation_id, consumer), 0) + 1
        self._by_method[(installation_id, method.upper())] = self._by_method.get((installation_id, method.upper()), 0) + 1

    def top_endpoints(self, installation_id: str, limit: int = 10) -> list[dict]:
        return self._top(self._by_endpoint, installation_id, limit)

    def top_consumers(self, installation_id: str, limit: int = 10) -> list[dict]:
        return self._top(self._by_consumer, installation_id, limit)

    def method_breakdown(self, installation_id: str) -> dict[str, int]:
        return {m: c for (inst, m), c in self._by_method.items() if inst == installation_id}

    def _top(self, store: dict, installation_id: str, limit: int) -> list[dict]:
        items = [(k, c) for (inst, k), c in store.items() if inst == installation_id]
        items.sort(key=lambda x: x[1], reverse=True)
        return [{"name": k, "count": c} for k, c in items[:limit]]
