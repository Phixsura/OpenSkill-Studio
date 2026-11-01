"""Deployment log streamer — capture and stream deploy logs."""
from __future__ import annotations
import time
import html

_logs: dict[str, list[dict]] = {}


def start_deploy(deploy_id: str) -> dict:
    _logs[deploy_id] = []
    return {"deploy_id": deploy_id, "started": True, "started_at": time.time()}


def append_log(deploy_id: str, level: str, message: str) -> dict:
    if deploy_id not in _logs:
        return {"appended": False, "error": "deploy_not_found"}
    entry = {"level": level, "message": html.escape(message),
             "timestamp": time.time(), "seq": len(_logs[deploy_id])}
    _logs[deploy_id].append(entry)
    return {"appended": True, "seq": entry["seq"]}


def get_logs(deploy_id: str, since_seq: int = 0) -> dict:
    logs = _logs.get(deploy_id, [])
    new_logs = [l for l in logs if l["seq"] >= since_seq]
    error_count = sum(1 for l in logs if l["level"] == "error")
    return {"deploy_id": deploy_id, "logs": new_logs, "total": len(logs),
            "new_count": len(new_logs), "error_count": error_count}


def clear_logs() -> None:
    _logs.clear()
