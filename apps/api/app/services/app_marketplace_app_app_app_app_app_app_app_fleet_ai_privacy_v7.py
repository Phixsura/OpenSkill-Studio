"""Fleet AI Privacy v7 — track ultimate data privacy management."""
from __future__ import annotations
def fleet_ai_privacy_v7(systems: list[dict]) -> dict:
    active = [s for s in systems if s.get("active", True)]
    pii_detected = sum(s.get("pii", 0) for s in systems)
    redacted = sum(s.get("redacted", 0) for s in systems)
    gdpr_compliant = all(s.get("gdpr", False) for s in systems)
    return {"systems": len(systems), "active": len(active), "pii": pii_detected,
            "redacted": redacted, "gdpr": gdpr_compliant, "private": gdpr_compliant and redacted >= pii_detected}
