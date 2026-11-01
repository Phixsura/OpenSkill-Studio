"""Fleet AI Privacy v8 — track ultimate data privacy at hyperscale."""
from __future__ import annotations
def fleet_ai_privacy_v8(systems: list[dict]) -> dict:
    active = [s for s in systems if s.get("active", True)]
    pii = sum(s.get("pii_detected", 0) for s in systems)
    redacted = sum(s.get("redacted", 0) for s in systems)
    gdpr = all(s.get("gdpr", False) for s in systems)
    ccpa = all(s.get("ccpa", False) for s in systems)
    return {"systems": len(systems), "active": len(active), "pii": pii,
            "redacted": redacted, "gdpr": gdpr, "ccpa": ccpa, "private": gdpr and ccpa}
