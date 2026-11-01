"""Fleet AI Audit v8 — track ultimate immutable audit trail."""
from __future__ import annotations
def fleet_ai_audit_v8(auditors: list[dict]) -> dict:
    active = [a for a in auditors if a.get("active", True)]
    events = sum(a.get("events_24h", 0) for a in auditors)
    retention = max((a.get("retention_days", 0) for a in auditors), default=0)
    tamper_proof = all(a.get("tamper_proof", False) for a in auditors)
    return {"auditors": len(auditors), "active": len(active), "events": events,
            "retention": retention, "tamper_proof": tamper_proof, "compliant": tamper_proof and retention >= 365}
