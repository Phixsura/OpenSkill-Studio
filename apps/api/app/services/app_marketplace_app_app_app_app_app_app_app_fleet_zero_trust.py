"""Fleet zero trust — track zero trust architecture adoption."""
from __future__ import annotations
def fleet_zero_trust(controls: list[dict]) -> dict:
    implemented = [c for c in controls if c.get("implemented", False)]
    score = round(len(implemented) / max(len(controls), 1) * 100, 1)
    return {"total": len(controls), "implemented": len(implemented),
            "remaining": len(controls) - len(implemented),
            "score": score, "mature": score >= 80}
