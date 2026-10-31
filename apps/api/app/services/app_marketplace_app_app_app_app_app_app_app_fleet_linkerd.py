"""Fleet Linkerd — track Linkerd service mesh health."""
from __future__ import annotations
def fleet_linkerd_status(namespaces: list[dict]) -> dict:
    meshed = [n for n in namespaces if n.get("meshed", False)]
    success_rate = round(sum(n.get("success_rate", 100) for n in meshed) / max(len(meshed), 1), 1)
    return {"total": len(namespaces), "meshed": len(meshed), "unmeshed": len(namespaces) - len(meshed),
            "avg_success_rate": success_rate, "healthy": success_rate >= 99}
