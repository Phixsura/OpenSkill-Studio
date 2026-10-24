"""Fleet API consistency — track naming and convention consistency."""
from __future__ import annotations
def fleet_api_consistency(endpoints: list[dict]) -> dict:
    consistent = [e for e in endpoints if e.get("follows_convention", True)]
    score = round(len(consistent) / max(len(endpoints), 1) * 100, 1)
    return {"total": len(endpoints), "consistent": len(consistent),
            "inconsistent": len(endpoints) - len(consistent), "score": score}
