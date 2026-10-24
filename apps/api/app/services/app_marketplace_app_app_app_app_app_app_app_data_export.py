"""Data export manager — manage bulk data exports in multiple formats."""
from __future__ import annotations
import time


class DataExportManager:
    def __init__(self):
        self._exports: dict[str, dict] = {}

    def create(self, export_id: str, format_type: str, query: str, requester: str) -> dict:
        self._exports[export_id] = {"id": export_id, "format": format_type,
                                     "query": query, "requester": requester,
                                     "status": "pending", "created_at": time.time(),
                                     "row_count": 0, "size_bytes": 0}
        return self._exports[export_id]

    def complete(self, export_id: str, row_count: int, size_bytes: int) -> dict:
        exp = self._exports[export_id]
        exp["status"] = "completed"
        exp["row_count"] = row_count
        exp["size_bytes"] = size_bytes
        return exp

    def fail(self, export_id: str, error: str) -> dict:
        self._exports[export_id]["status"] = "failed"
        self._exports[export_id]["error"] = error
        return {"id": export_id, "status": "failed"}

    def list_exports(self, status: str = "") -> list[dict]:
        exports = list(self._exports.values())
        if status:
            exports = [e for e in exports if e["status"] == status]
        return exports

    def stats(self) -> dict:
        by_status = {}
        for e in self._exports.values():
            by_status[e["status"]] = by_status.get(e["status"], 0) + 1
        total_bytes = sum(e["size_bytes"] for e in self._exports.values())
        return {"total": len(self._exports), "by_status": by_status,
                "total_bytes": total_bytes}
