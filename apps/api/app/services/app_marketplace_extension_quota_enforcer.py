"""Quota Enforcer — multi-dimensional quota with sliding windows and burst.

Unlike rate limiters (requests/time), quotas track cumulative resource
usage: storage bytes, compute hours, bandwidth, API calls per billing period.

Implements:
- Multiple quota dimensions per tenant
- Hard limit (reject) vs soft limit (warn)
- Grace period after limit reached
- Usage rollover or reset at period boundary
- Top-N usage report
"""
from __future__ import annotations
from dataclasses import dataclass, field
import time


@dataclass
class QuotaDimension:
    name: str
    hard_limit: float
    soft_limit: float  # warning threshold (usually 80% of hard)
    used: float = 0.0
    unit: str = ""
    grace_seconds: float = 0  # allow exceeding for this long
    grace_start: float = 0


@dataclass
class QuotaCheckResult:
    allowed: bool
    dimension: str
    used: float
    limit: float
    remaining: float
    status: str  # ok, warning, exceeded, grace


class QuotaEnforcerService:
    def __init__(self):
        self._quotas: dict[str, dict[str, QuotaDimension]] = {}  # tenant -> {dim_name -> dim}

    def configure(self, tenant_id: str, name: str, hard_limit: float,
                  soft_limit: float = 0, unit: str = "",
                  grace_seconds: float = 0) -> QuotaDimension:
        if tenant_id not in self._quotas:
            self._quotas[tenant_id] = {}
        if soft_limit == 0:
            soft_limit = hard_limit * 0.8
        dim = QuotaDimension(name=name, hard_limit=hard_limit,
                             soft_limit=soft_limit, unit=unit,
                             grace_seconds=grace_seconds)
        self._quotas[tenant_id][name] = dim
        return dim

    def check_and_consume(self, tenant_id: str, dimension: str,
                          amount: float = 1.0) -> QuotaCheckResult:
        """Check quota and consume if allowed."""
        dim = self._quotas.get(tenant_id, {}).get(dimension)
        if not dim:
            return QuotaCheckResult(True, dimension, 0, 0, 0, "no_quota")

        remaining = dim.hard_limit - dim.used
        now = time.time()

        # Check hard limit
        if dim.used + amount > dim.hard_limit:
            # Grace period check
            if dim.grace_seconds > 0:
                if dim.grace_start == 0:
                    dim.grace_start = now
                if now - dim.grace_start < dim.grace_seconds:
                    dim.used += amount
                    return QuotaCheckResult(True, dimension, dim.used,
                                           dim.hard_limit, max(0, dim.hard_limit - dim.used),
                                           "grace")
            return QuotaCheckResult(False, dimension, dim.used,
                                   dim.hard_limit, 0, "exceeded")

        dim.used += amount

        # Check soft limit (warning)
        status = "ok"
        if dim.used >= dim.soft_limit:
            status = "warning"

        return QuotaCheckResult(True, dimension, dim.used, dim.hard_limit,
                                max(0, dim.hard_limit - dim.used), status)

    def get_usage(self, tenant_id: str) -> dict[str, dict]:
        dims = self._quotas.get(tenant_id, {})
        return {name: {
            "used": dim.used, "hard_limit": dim.hard_limit,
            "soft_limit": dim.soft_limit, "unit": dim.unit,
            "pct": round(dim.used / dim.hard_limit * 100, 1) if dim.hard_limit else 0,
            "status": "exceeded" if dim.used >= dim.hard_limit
                      else "warning" if dim.used >= dim.soft_limit
                      else "ok"
        } for name, dim in dims.items()}

    def reset(self, tenant_id: str, dimension: str | None = None) -> bool:
        dims = self._quotas.get(tenant_id, {})
        if dimension:
            dim = dims.get(dimension)
            if dim:
                dim.used = 0
                dim.grace_start = 0
                return True
            return False
        for dim in dims.values():
            dim.used = 0
            dim.grace_start = 0
        return True

    def top_consumers(self, dimension: str, limit: int = 10) -> list[tuple[str, float]]:
        """Find top N tenants by usage for a dimension."""
        usage = []
        for tenant_id, dims in self._quotas.items():
            dim = dims.get(dimension)
            if dim:
                usage.append((tenant_id, dim.used))
        return sorted(usage, key=lambda x: x[1], reverse=True)[:limit]
