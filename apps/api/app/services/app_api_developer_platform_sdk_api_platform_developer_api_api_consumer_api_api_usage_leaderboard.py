"""API Consumer Usage Leaderboard — rank consumers by API usage metrics."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class LeaderboardEntry:
    rank: int
    consumer_id: str
    total_requests: int
    success_rate: float
    avg_latency_ms: float
    score: float  # composite score

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiUsageLeaderboard:
    def __init__(self) -> None:
        self._data: dict[tuple[str, str], dict[str, float]] = {}

    def record_usage(self, installation_id: str, consumer_id: str, requests: int, successes: int, total_latency_ms: float) -> None:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, consumer_id)
        d = self._data.get(key, {"requests": 0, "successes": 0, "total_latency": 0})
        d["requests"] += requests
        d["successes"] += successes
        d["total_latency"] += total_latency_ms
        self._data[key] = d

    def leaderboard(self, installation_id: str, limit: int = 10) -> list[LeaderboardEntry]:
        entries = []
        for (inst, cid), d in self._data.items():
            if inst != installation_id: continue
            reqs = d["requests"]
            sr = round((d["successes"] / reqs) * 100, 1) if reqs > 0 else 0
            avg_lat = round(d["total_latency"] / reqs, 1) if reqs > 0 else 0
            score = round(reqs * (sr / 100) / max(1, avg_lat / 100), 1)
            entries.append(LeaderboardEntry(rank=0, consumer_id=cid, total_requests=reqs, success_rate=sr, avg_latency_ms=avg_lat, score=score))
        entries.sort(key=lambda e: -e.score)
        for i, e in enumerate(entries): e.rank = i + 1
        return entries[:limit]

    def consumer_rank(self, installation_id: str, consumer_id: str) -> int | None:
        lb = self.leaderboard(installation_id, limit=9999)
        for e in lb:
            if e.consumer_id == consumer_id: return e.rank
        return None

    def consumer_count(self, installation_id: str) -> int:
        return sum(1 for (inst, _) in self._data if inst == installation_id)
