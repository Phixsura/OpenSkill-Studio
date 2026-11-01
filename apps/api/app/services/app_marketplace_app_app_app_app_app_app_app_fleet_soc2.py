"""Fleet SOC2 readiness — track SOC2 control implementation."""
from __future__ import annotations
def fleet_soc2_readiness(controls: list[dict]) -> dict:
    implemented = [c for c in controls if c.get("implemented", False)]
    tested = [c for c in controls if c.get("tested", False)]
    return {"total": len(controls), "implemented": len(implemented),
            "tested": len(tested), "ready": len(tested) == len(controls)}
