"""Fleet SBOM generation — track software bill of materials coverage."""
from __future__ import annotations
def fleet_sbom_generation(artifacts: list[dict]) -> dict:
    with_sbom = [a for a in artifacts if a.get("has_sbom", False)]
    formats = list(set(a.get("sbom_format", "") for a in with_sbom if a.get("sbom_format")))
    pct = round(len(with_sbom) / max(len(artifacts), 1) * 100, 1)
    return {"total": len(artifacts), "with_sbom": len(with_sbom), "formats": formats,
            "coverage_pct": pct, "compliant": pct >= 95}
