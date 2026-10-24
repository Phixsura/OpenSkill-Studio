"""Fleet image pull — track container image pull times."""
from __future__ import annotations
def fleet_image_pull(pulls: list[dict]) -> dict:
    avg_ms = round(sum(p.get("pull_ms", 0) for p in pulls) / max(len(pulls), 1), 1)
    slow = [p for p in pulls if p.get("pull_ms", 0) > 30000]
    failed = [p for p in pulls if p.get("status") == "failed"]
    return {"total": len(pulls), "avg_pull_ms": avg_ms, "slow_pulls": len(slow),
            "failed": len(failed), "healthy": len(failed) == 0}
