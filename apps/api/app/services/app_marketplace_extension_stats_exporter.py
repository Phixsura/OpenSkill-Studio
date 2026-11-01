"""Marketplace Stats Exporter — export platform statistics."""
from __future__ import annotations
import json
import time


class MktplaceStatsExporterService:
    def __init__(self):
        self._snapshots: list[dict] = []

    def capture(self, stats: dict) -> dict:
        snapshot = {"timestamp": time.time(), "data": dict(stats)}
        self._snapshots.append(snapshot)
        return snapshot

    def export_json(self, limit: int = 100) -> str:
        data = self._snapshots[-limit:]
        return json.dumps(data, indent=2)

    def export_csv(self, keys: list[str]) -> str:
        if not self._snapshots:
            return ",".join(["timestamp"] + keys) + "\n"
        lines = [",".join(["timestamp"] + keys)]
        for snap in self._snapshots:
            row = [str(snap["timestamp"])]
            for k in keys:
                row.append(str(snap["data"].get(k, "")))
            lines.append(",".join(row))
        return "\n".join(lines)

    def get_trend(self, key: str) -> list[tuple[float, float]]:
        return [(s["timestamp"], s["data"].get(key, 0)) for s in self._snapshots
                if key in s["data"]]

    def get_latest(self) -> dict | None:
        return self._snapshots[-1] if self._snapshots else None
