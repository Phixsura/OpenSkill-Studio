"""Fleet secret scanning — detect leaked secrets in code."""
from __future__ import annotations
def fleet_secret_scan(repos: list[dict]) -> dict:
    clean = [r for r in repos if r.get("secrets_found", 0) == 0]
    total_secrets = sum(r.get("secrets_found", 0) for r in repos)
    return {"total_repos": len(repos), "clean": len(clean), "leaked": total_secrets,
            "all_clean": total_secrets == 0}
