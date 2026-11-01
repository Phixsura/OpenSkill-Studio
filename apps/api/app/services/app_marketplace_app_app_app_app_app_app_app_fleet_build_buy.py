"""Fleet build vs buy — track internal vs vendor component ratio."""
from __future__ import annotations
def fleet_build_vs_buy(components: list[dict]) -> dict:
    built = [c for c in components if c.get("source") == "built"]
    bought = [c for c in components if c.get("source") == "bought"]
    oss = [c for c in components if c.get("source") == "oss"]
    return {"total": len(components), "built": len(built), "bought": len(bought),
            "oss": len(oss), "build_ratio": round(len(built) / max(len(components), 1) * 100, 1)}
