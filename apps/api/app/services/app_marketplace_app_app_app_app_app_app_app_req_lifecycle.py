"""Request lifecycle tracker — track request through all processing stages."""
from __future__ import annotations
import time


class RequestLifecycle:
    def __init__(self):
        self._requests: dict[str, dict] = {}

    def start(self, request_id: str) -> dict:
        self._requests[request_id] = {"id": request_id, "stages": [], "started_at": time.time()}
        return {"request_id": request_id, "started": True}

    def add_stage(self, request_id: str, stage: str, duration_ms: float, status: str = "ok") -> dict:
        req = self._requests.get(request_id)
        if not req:
            return {"error": "request_not_found"}
        req["stages"].append({"stage": stage, "duration_ms": duration_ms, "status": status})
        return {"request_id": request_id, "stage": stage, "total_stages": len(req["stages"])}

    def complete(self, request_id: str) -> dict:
        req = self._requests.get(request_id)
        if not req:
            return {"error": "request_not_found"}
        total_ms = sum(s["duration_ms"] for s in req["stages"])
        failed = any(s["status"] == "error" for s in req["stages"])
        return {"request_id": request_id, "total_ms": round(total_ms, 1),
                "stages": len(req["stages"]), "success": not failed,
                "breakdown": req["stages"]}

    def stats(self) -> dict:
        return {"tracked_requests": len(self._requests)}
