"""Fleet AI Secret Scanner — track credential and secret detection in code."""
from __future__ import annotations
def fleet_ai_secret_scanner(scanners: list[dict]) -> dict:
    active = [s for s in scanners if s.get("active", True)]
    repos_scanned = sum(s.get("repos", 0) for s in scanners)
    secrets_found = sum(s.get("secrets_found", 0) for s in scanners)
    revoked = sum(s.get("revoked", 0) for s in scanners)
    return {"scanners": len(scanners), "active": len(active), "repos": repos_scanned,
            "secrets_found": secrets_found, "revoked": revoked, "clean": secrets_found == revoked}
