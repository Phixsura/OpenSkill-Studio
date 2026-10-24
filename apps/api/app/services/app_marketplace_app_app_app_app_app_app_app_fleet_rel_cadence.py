"""Fleet release cadence — track release frequency and regularity."""
from __future__ import annotations
def fleet_release_cadence(releases: list[dict]) -> dict:
    total = len(releases)
    if total < 2:
        return {"total": total, "avg_gap_days": 0, "regular": False}
    gaps = [releases[i+1].get("day", 0) - releases[i].get("day", 0) for i in range(total - 1)]
    avg_gap = round(sum(gaps) / len(gaps), 1)
    return {"total": total, "avg_gap_days": avg_gap, "regular": avg_gap <= 14}
