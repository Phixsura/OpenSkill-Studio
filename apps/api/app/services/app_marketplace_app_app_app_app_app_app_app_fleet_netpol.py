"""Fleet network policy — track network policy coverage."""
from __future__ import annotations
def fleet_netpol(namespaces: list[dict]) -> dict:
    covered = [n for n in namespaces if n.get("has_netpol", False)]
    return {"total": len(namespaces), "covered": len(covered),
            "uncovered": len(namespaces) - len(covered),
            "full_coverage": len(covered) == len(namespaces)}
