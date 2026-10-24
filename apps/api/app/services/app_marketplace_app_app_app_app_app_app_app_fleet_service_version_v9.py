"""Fleet Service Version v9 — track deployed service versions across envs."""
from __future__ import annotations
def fleet_service_version_v9(services: list[dict]) -> dict:
    latest = [s for s in services if s.get("on_latest")]
    outdated = [s for s in services if not s.get("on_latest")]
    versions = len({s.get("version") for s in services if s.get("version")})
    return {"services": len(services), "on_latest": len(latest), "outdated": len(outdated),
            "unique_versions": versions, "healthy": len(outdated) < len(services) * 0.1}
