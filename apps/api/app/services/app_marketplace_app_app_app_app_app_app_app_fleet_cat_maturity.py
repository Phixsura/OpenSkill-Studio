"""Fleet catalog maturity — track service catalog completeness."""
from __future__ import annotations
def fleet_catalog_maturity(services: list[dict]) -> dict:
    with_all = [s for s in services if s.get("has_owner") and s.get("has_docs") and s.get("has_runbook") and s.get("has_slo")]
    pct = round(len(with_all) / max(len(services), 1) * 100, 1)
    return {"total": len(services), "fully_cataloged": len(with_all),
            "partial": len(services) - len(with_all), "maturity_pct": pct, "mature": pct >= 80}
