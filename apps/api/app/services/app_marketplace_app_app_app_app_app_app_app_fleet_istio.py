"""Fleet Istio — track Istio service mesh status."""
from __future__ import annotations
def fleet_istio_status(proxies: list[dict]) -> dict:
    synced = [p for p in proxies if p.get("config_synced", True)]
    version_mismatch = [p for p in proxies if p.get("version") != proxies[0].get("version")] if proxies else []
    return {"total": len(proxies), "synced": len(synced), "out_of_sync": len(proxies) - len(synced),
            "version_mismatch": len(version_mismatch), "healthy": len(synced) == len(proxies)}
