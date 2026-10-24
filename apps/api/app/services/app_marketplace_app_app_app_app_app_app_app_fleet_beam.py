"""Fleet Beam — track unified batch/stream pipeline health."""
from __future__ import annotations
def fleet_beam_status(pipelines: list[dict]) -> dict:
    running = [p for p in pipelines if p.get("state") == "RUNNING"]
    drained = [p for p in pipelines if p.get("state") == "DRAINED"]
    failed = [p for p in pipelines if p.get("state") == "FAILED"]
    return {"total": len(pipelines), "running": len(running), "drained": len(drained),
            "failed": len(failed), "healthy": len(failed) == 0}
