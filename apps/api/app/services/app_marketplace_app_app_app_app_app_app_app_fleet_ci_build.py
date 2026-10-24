"""Fleet CI build time — track build duration trends."""
from __future__ import annotations
def fleet_ci_build_time(builds: list[dict]) -> dict:
    times = [b.get("duration_sec", 0) for b in builds]
    avg = round(sum(times) / max(len(times), 1), 1)
    slow = [t for t in times if t > 600]
    return {"total": len(builds), "avg_sec": avg, "slow_builds": len(slow),
            "fast": avg <= 300}
