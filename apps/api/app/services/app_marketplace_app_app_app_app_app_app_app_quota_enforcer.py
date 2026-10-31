"""Quota enforcement engine — enforce hard and soft limits across resources."""
from __future__ import annotations


class QuotaEnforcer:
    def __init__(self):
        self._quotas: dict[str, dict] = {}

    def set_quota(self, resource: str, *, hard_limit: int, soft_limit: int | None = None,
                   unit: str = "count") -> dict:
        soft = soft_limit or int(hard_limit * 0.8)
        self._quotas[resource] = {"hard": hard_limit, "soft": soft, "unit": unit, "usage": 0}
        return {"resource": resource, "hard_limit": hard_limit, "soft_limit": soft}

    def consume(self, resource: str, amount: int = 1) -> dict:
        q = self._quotas.get(resource)
        if not q:
            return {"allowed": True, "reason": "no_quota"}
        new_usage = q["usage"] + amount
        if new_usage > q["hard"]:
            return {"allowed": False, "reason": "hard_limit_exceeded",
                    "usage": q["usage"], "limit": q["hard"]}
        q["usage"] = new_usage
        warning = new_usage >= q["soft"]
        return {"allowed": True, "usage": new_usage, "limit": q["hard"],
                "warning": warning, "pct": round(new_usage / q["hard"] * 100, 1),
                "reason": "soft_limit_warning" if warning else "ok"}

    def reset(self, resource: str) -> dict:
        q = self._quotas.get(resource)
        if not q:
            return {"error": "Quota not found"}
        q["usage"] = 0
        return {"resource": resource, "reset": True}

    def summary(self) -> dict:
        items = []
        for r, q in self._quotas.items():
            pct = round(q["usage"] / max(q["hard"], 1) * 100, 1)
            items.append({"resource": r, "usage": q["usage"], "hard": q["hard"],
                          "soft": q["soft"], "pct": pct, "unit": q["unit"],
                          "status": "exceeded" if q["usage"] > q["hard"] else "warning" if q["usage"] >= q["soft"] else "ok"})
        return {"quotas": items, "total": len(items)}
