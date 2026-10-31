"""Service mesh retry budget — manage retry budgets per service pair."""
from __future__ import annotations
from collections import defaultdict


class MeshRetryBudget:
    def __init__(self, budget_pct: float = 20):
        self._budget_pct = budget_pct
        self._stats: dict[str, dict] = defaultdict(lambda: {"requests": 0, "retries": 0})

    def record_request(self, source: str, destination: str, is_retry: bool = False) -> dict:
        key = f"{source}→{destination}"
        self._stats[key]["requests"] += 1
        if is_retry:
            self._stats[key]["retries"] += 1
        return {"key": key, "is_retry": is_retry}

    def check_budget(self, source: str, destination: str) -> dict:
        key = f"{source}→{destination}"
        s = self._stats.get(key, {"requests": 0, "retries": 0})
        budget = round(s["requests"] * self._budget_pct / 100)
        used_pct = round(s["retries"] / max(budget, 1) * 100, 1)
        exhausted = s["retries"] >= budget and budget > 0
        return {"key": key, "budget": budget, "used": s["retries"],
                "used_pct": used_pct, "exhausted": exhausted,
                "can_retry": not exhausted}

    def all_budgets(self) -> list[dict]:
        return [self.check_budget(*k.split("→")) for k in self._stats]
