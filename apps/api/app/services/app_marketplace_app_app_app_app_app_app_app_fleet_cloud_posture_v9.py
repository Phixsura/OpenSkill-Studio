"""Fleet Cloud Posture v9 — track cloud security posture management (CSPM)."""
from __future__ import annotations
def fleet_cloud_posture_v9(accounts: list[dict]) -> dict:
    compliant = [a for a in accounts if a.get("compliant")]
    misconfigs = sum(a.get("misconfigurations", 0) for a in accounts)
    score = sum(a.get("score", 0) for a in accounts) / len(accounts) if accounts else 0
    return {"accounts": len(accounts), "compliant": len(compliant), "misconfigurations": misconfigs,
            "avg_score": round(score, 1), "healthy": misconfigs == 0}
