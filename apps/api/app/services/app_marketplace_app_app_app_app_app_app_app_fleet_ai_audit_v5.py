"""Fleet AI Audit v5 — track immutable audit trail at enterprise scale."""
from __future__ import annotations
def fleet_ai_audit_v5(auditors: list[dict]) -> dict:
    active = [a for a in auditors if a.get("active", True)]
    events_24h = sum(a.get("events", 0) for a in auditors)
    retention_days = max((a.get("retention", 0) for a in auditors), default=0)
    tamper_proof = all(a.get("tamper_proof", False) for a in auditors)
    return {"auditors": len(auditors), "active": len(active), "events_24h": events_24h,
            "retention_days": retention_days, "tamper_proof": tamper_proof, "compliant": tamper_proof and retention_days >= 365}
