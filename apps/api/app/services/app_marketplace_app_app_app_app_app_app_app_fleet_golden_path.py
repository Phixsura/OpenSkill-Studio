"""Fleet golden path — track golden path template adoption."""
from __future__ import annotations
def fleet_golden_path(services: list[dict]) -> dict:
    on_path = [s for s in services if s.get("uses_golden_path", False)]
    pct = round(len(on_path) / max(len(services), 1) * 100, 1)
    return {"total": len(services), "on_golden_path": len(on_path),
            "off_path": len(services) - len(on_path), "adoption_pct": pct}
