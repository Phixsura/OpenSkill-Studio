"""Fleet API versioning — track API version distribution."""
from __future__ import annotations
def fleet_api_versions(apis: list[dict]) -> dict:
    versions: dict[str, int] = {}
    for a in apis:
        v = a.get("version", "unknown")
        versions[v] = versions.get(v, 0) + 1
    deprecated = [a for a in apis if a.get("deprecated", False)]
    return {"total": len(apis), "versions": versions,
            "deprecated": len(deprecated), "needs_migration": len(deprecated) > 0}
