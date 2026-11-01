"""Fleet Pod Security v9 — track pod security standards enforcement."""
from __future__ import annotations
def fleet_pod_security_v9(namespaces: list[dict]) -> dict:
    restricted = [n for n in namespaces if n.get("level") == "restricted"]
    baseline = [n for n in namespaces if n.get("level") == "baseline"]
    privileged = [n for n in namespaces if n.get("level") == "privileged"]
    return {"namespaces": len(namespaces), "restricted": len(restricted), "baseline": len(baseline),
            "privileged": len(privileged), "healthy": len(privileged) == 0}
