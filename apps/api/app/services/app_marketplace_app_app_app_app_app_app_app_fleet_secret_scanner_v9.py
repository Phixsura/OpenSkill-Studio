"""Fleet Secret Scanner v9 — track secret leak detection in code."""
from __future__ import annotations
def fleet_secret_scanner_v9(repos: list[dict]) -> dict:
    scanned = [r for r in repos if r.get("scanned")]
    secrets_found = sum(r.get("secrets_found", 0) for r in repos)
    remediated = sum(r.get("remediated", 0) for r in repos)
    return {"repos": len(repos), "scanned": len(scanned), "secrets_found": secrets_found,
            "remediated": remediated, "healthy": secrets_found == remediated}
