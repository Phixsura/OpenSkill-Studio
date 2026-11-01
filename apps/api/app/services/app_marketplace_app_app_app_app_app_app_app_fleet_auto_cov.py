"""Fleet automation coverage — track what's automated vs manual."""
from __future__ import annotations
def fleet_automation_coverage(processes: list[dict]) -> dict:
    automated = [p for p in processes if p.get("automated", False)]
    manual = len(processes) - len(automated)
    pct = round(len(automated) / max(len(processes), 1) * 100, 1)
    return {"total": len(processes), "automated": len(automated), "manual": manual,
            "coverage_pct": pct, "mature": pct >= 80}
