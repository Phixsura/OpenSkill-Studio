"""Fleet AI PII Redaction — track personal data protection."""
from __future__ import annotations
def fleet_ai_pii(services: list[dict]) -> dict:
    active = [s for s in services if s.get("active", True)]
    docs_scanned = sum(s.get("docs_24h", 0) for s in services)
    pii_found = sum(s.get("pii_found_24h", 0) for s in services)
    redacted = sum(s.get("redacted_24h", 0) for s in services)
    return {"services": len(services), "active": len(active), "docs_24h": docs_scanned,
            "pii_found": pii_found, "redacted": redacted, "all_redacted": pii_found == redacted}
