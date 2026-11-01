"""Fleet SPIFFE — track workload identity federation."""
from __future__ import annotations
def fleet_spiffe_status(workloads: list[dict]) -> dict:
    with_svid = [w for w in workloads if w.get("has_svid", False)]
    expired = [w for w in workloads if w.get("svid_expired", False)]
    return {"total": len(workloads), "with_svid": len(with_svid), "expired": len(expired),
            "coverage_pct": round(len(with_svid) / max(len(workloads), 1) * 100, 1),
            "healthy": len(expired) == 0}
