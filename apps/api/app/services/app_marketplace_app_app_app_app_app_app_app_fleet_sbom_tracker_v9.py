"""Fleet SBOM Tracker v9 — track software bill of materials compliance."""
from __future__ import annotations
def fleet_sbom_tracker_v9(artifacts: list[dict]) -> dict:
    with_sbom = [a for a in artifacts if a.get("sbom_generated")]
    licenses_ok = [a for a in artifacts if a.get("license_compliant")]
    components = sum(a.get("components", 0) for a in artifacts)
    return {"artifacts": len(artifacts), "with_sbom": len(with_sbom), "license_compliant": len(licenses_ok),
            "total_components": components, "healthy": len(with_sbom) == len(artifacts)}
