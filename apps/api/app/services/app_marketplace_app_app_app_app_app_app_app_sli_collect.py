"""SLI collector — collect and aggregate service level indicators."""
from __future__ import annotations
from collections import defaultdict


class SliCollector:
    def __init__(self):
        self._indicators: dict[str, list[float]] = defaultdict(list)

    def record(self, sli_name: str, value: float) -> dict:
        self._indicators[sli_name].append(value)
        return {"sli": sli_name, "recorded": True, "count": len(self._indicators[sli_name])}

    def summary(self, sli_name: str) -> dict:
        values = self._indicators.get(sli_name, [])
        if not values:
            return {"sli": sli_name, "count": 0}
        s = sorted(values)
        n = len(s)
        return {"sli": sli_name, "count": n, "min": s[0], "max": s[-1],
                "avg": round(sum(s) / n, 3),
                "p50": s[n // 2], "p99": s[int(n * 0.99)],
                "good_pct": round(sum(1 for v in values if v <= s[int(n * 0.95)]) / n * 100, 1)}

    def all_slis(self) -> list[dict]:
        return [self.summary(name) for name in sorted(self._indicators)]

    def compliance(self, sli_name: str, target: float, good_threshold: float) -> dict:
        values = self._indicators.get(sli_name, [])
        if not values:
            return {"sli": sli_name, "compliant": True, "good_pct": 100}
        good = sum(1 for v in values if v <= good_threshold)
        good_pct = round(good / len(values) * 100, 2)
        return {"sli": sli_name, "compliant": good_pct >= target,
                "good_pct": good_pct, "target": target}
