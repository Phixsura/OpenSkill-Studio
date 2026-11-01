"""Fleet Image Builder v9 — track container image build pipelines."""
from __future__ import annotations
def fleet_image_builder_v9(builds: list[dict]) -> dict:
    success = [b for b in builds if b.get("status") == "success"]
    failed = [b for b in builds if b.get("status") == "failed"]
    avg_time = sum(b.get("build_time_sec", 0) for b in builds) / len(builds) if builds else 0
    return {"total": len(builds), "success": len(success), "failed": len(failed),
            "avg_build_time_sec": round(avg_time, 1), "healthy": len(failed) == 0}
