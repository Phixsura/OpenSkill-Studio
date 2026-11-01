"""Traffic mirror — mirror production traffic to shadow environments."""
from __future__ import annotations


class TrafficMirror:
    def __init__(self):
        self._mirrors: dict[str, dict] = {}
        self._mirrored_count = 0

    def create_mirror(self, source: str, target: str, sample_pct: int = 100) -> dict:
        key = f"{source}→{target}"
        self._mirrors[key] = {"source": source, "target": target,
                               "sample_pct": sample_pct, "active": True,
                               "mirrored": 0, "errors": 0}
        return self._mirrors[key]

    def mirror_request(self, source: str) -> list[dict]:
        results = []
        for key, m in self._mirrors.items():
            if m["source"] == source and m["active"]:
                m["mirrored"] += 1
                self._mirrored_count += 1
                results.append({"target": m["target"], "mirrored": True})
        return results

    def pause(self, source: str, target: str) -> dict:
        key = f"{source}→{target}"
        self._mirrors[key]["active"] = False
        return {"paused": True}

    def stats(self) -> dict:
        active = sum(1 for m in self._mirrors.values() if m["active"])
        return {"total_mirrors": len(self._mirrors), "active": active,
                "total_mirrored": self._mirrored_count}
