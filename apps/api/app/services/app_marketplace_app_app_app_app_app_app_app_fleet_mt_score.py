"""Fleet multitenancy score — assess tenant isolation quality."""
from __future__ import annotations
def fleet_mt_score(dimensions: dict) -> dict:
    data_iso = dimensions.get("data_isolation", 0)
    compute_iso = dimensions.get("compute_isolation", 0)
    network_iso = dimensions.get("network_isolation", 0)
    score = round((data_iso + compute_iso + network_iso) / 3, 1)
    return {"score": score, "data": data_iso, "compute": compute_iso, "network": network_iso,
            "enterprise_ready": score >= 90}
