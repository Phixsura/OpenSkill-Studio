"""Deployment freeze manager — block deploys during freeze windows."""
from __future__ import annotations
import time


_freezes: list[dict] = []


def create_freeze(reason: str, start_ts: float, end_ts: float, environments: list[str] | None = None) -> dict:
    freeze = {"id": len(_freezes) + 1, "reason": reason, "start_ts": start_ts,
              "end_ts": end_ts, "environments": environments or ["production"],
              "created_at": time.time(), "active": True}
    _freezes.append(freeze)
    return freeze


def is_frozen(environment: str = "production", now: float | None = None) -> dict:
    now = now or time.time()
    active = [f for f in _freezes if f["active"] and f["start_ts"] <= now <= f["end_ts"]
              and environment in f["environments"]]
    if active:
        return {"frozen": True, "reason": active[0]["reason"],
                "ends_at": active[0]["end_ts"], "freeze_count": len(active)}
    return {"frozen": False}


def list_freezes() -> list[dict]:
    return list(_freezes)


def cancel_freeze(freeze_id: int) -> dict:
    for f in _freezes:
        if f["id"] == freeze_id:
            f["active"] = False
            return {"cancelled": True}
    return {"cancelled": False, "error": "not_found"}


def clear_freezes() -> None:
    _freezes.clear()
