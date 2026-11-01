"""Fleet toil tracker — measure toil vs engineering work."""
from __future__ import annotations
def fleet_toil_summary(teams: list[dict]) -> dict:
    total_toil = sum(t.get("toil_hours", 0) for t in teams)
    total_eng = sum(t.get("eng_hours", 0) for t in teams)
    total = total_toil + total_eng
    toil_pct = round(total_toil / max(total, 1) * 100, 1)
    return {"toil_hours": total_toil, "eng_hours": total_eng,
            "toil_pct": toil_pct, "acceptable": toil_pct <= 50}
