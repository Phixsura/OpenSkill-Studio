"""Fleet SLI tracker — service level indicator aggregation."""
from __future__ import annotations
def fleet_sli_summary(slis: list[dict]) -> dict:
    meeting = [s for s in slis if s.get("current", 0) >= s.get("target", 100)]
    return {"total": len(slis), "meeting_target": len(meeting),
            "missing_target": len(slis) - len(meeting),
            "compliance_pct": round(len(meeting) / max(len(slis), 1) * 100, 1)}
