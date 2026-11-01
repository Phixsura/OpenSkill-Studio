"""Slow query detector — detect and track slow database queries."""
from __future__ import annotations
from collections import defaultdict


class SlowQueryDetector:
    def __init__(self, threshold_ms: float = 100):
        self._threshold = threshold_ms
        self._queries: list[dict] = []

    def record(self, query: str, duration_ms: float, table: str = "") -> dict:
        is_slow = duration_ms >= self._threshold
        entry = {"query": query[:200], "duration_ms": duration_ms,
                 "table": table, "slow": is_slow}
        if is_slow:
            self._queries.append(entry)
        return entry

    def top_slow(self, limit: int = 10) -> list[dict]:
        return sorted(self._queries, key=lambda q: -q["duration_ms"])[:limit]

    def by_table(self) -> dict:
        tables: dict[str, dict] = defaultdict(lambda: {"count": 0, "total_ms": 0})
        for q in self._queries:
            t = q.get("table", "unknown")
            tables[t]["count"] += 1
            tables[t]["total_ms"] += q["duration_ms"]
        return {k: {**v, "avg_ms": round(v["total_ms"] / max(v["count"], 1), 1)}
                for k, v in sorted(tables.items(), key=lambda x: -x[1]["total_ms"])}

    def stats(self) -> dict:
        return {"slow_queries": len(self._queries), "threshold_ms": self._threshold}
