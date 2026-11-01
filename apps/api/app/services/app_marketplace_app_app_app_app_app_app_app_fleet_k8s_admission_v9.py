"""Fleet K8s Admission v9 — track admission controller webhook enforcement."""
from __future__ import annotations
def fleet_k8s_admission_v9(webhooks: list[dict]) -> dict:
    validating = [w for w in webhooks if w.get("type") == "validating"]
    mutating = [w for w in webhooks if w.get("type") == "mutating"]
    denied = sum(w.get("denied_today", 0) for w in webhooks)
    return {"webhooks": len(webhooks), "validating": len(validating), "mutating": len(mutating),
            "denied_today": denied, "healthy": True}
