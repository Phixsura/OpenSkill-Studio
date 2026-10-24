"""Fleet supply chain security — SBOM and provenance tracking."""
from __future__ import annotations
def fleet_supply_chain(artifacts: list[dict]) -> dict:
    with_sbom = [a for a in artifacts if a.get("has_sbom", False)]
    signed = [a for a in artifacts if a.get("signed", False)]
    with_provenance = [a for a in artifacts if a.get("has_provenance", False)]
    return {"total": len(artifacts), "with_sbom": len(with_sbom),
            "signed": len(signed), "with_provenance": len(with_provenance),
            "secure": len(with_sbom) == len(artifacts) and len(signed) == len(artifacts)}
