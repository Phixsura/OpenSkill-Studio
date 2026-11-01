"""Fleet Immutable Infra v9 — track immutable infrastructure compliance."""
from __future__ import annotations
def fleet_immutable_infra_v9(instances: list[dict]) -> dict:
    immutable = [i for i in instances if i.get("immutable")]
    mutable = [i for i in instances if not i.get("immutable")]
    avg_age = sum(i.get("age_hours", 0) for i in instances) / len(instances) if instances else 0
    return {"instances": len(instances), "immutable": len(immutable), "mutable": len(mutable),
            "avg_age_hours": round(avg_age, 1), "healthy": len(mutable) == 0}
