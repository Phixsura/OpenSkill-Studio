"""Fleet Binary Artifact v9 — track build artifact storage and distribution."""
from __future__ import annotations
def fleet_binary_artifact_v9(artifacts: list[dict]) -> dict:
    signed = [a for a in artifacts if a.get("signed")]
    size_gb = sum(a.get("size_mb", 0) for a in artifacts) / 1024
    downloads = sum(a.get("downloads", 0) for a in artifacts)
    return {"total": len(artifacts), "signed": len(signed), "size_gb": round(size_gb, 1),
            "total_downloads": downloads, "healthy": len(signed) == len(artifacts)}
