"""Fleet Deployment Window v9 — track deployment window scheduling."""
from __future__ import annotations
def fleet_deployment_window_v9(windows: list[dict]) -> dict:
    open_w = [w for w in windows if w.get("status") == "open"]
    closed = [w for w in windows if w.get("status") == "closed"]
    frozen = [w for w in windows if w.get("status") == "frozen"]
    return {"windows": len(windows), "open": len(open_w), "closed": len(closed),
            "frozen": len(frozen), "healthy": len(frozen) == 0}
