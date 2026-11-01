"""App API Developer Leaderboard — rank developers by platform engagement."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class LeaderboardEntry:
    developer_id: str
    display_name: str
    api_calls: int = 0
    apps_created: int = 0
    webhooks_configured: int = 0
    docs_contributed: int = 0

    @property
    def total_score(self) -> int:
        return self.api_calls // 100 + self.apps_created * 50 + self.webhooks_configured * 20 + self.docs_contributed * 30

    @property
    def rank_tier(self) -> str:
        s = self.total_score
        if s >= 1000: return "diamond"
        if s >= 500: return "platinum"
        if s >= 200: return "gold"
        if s >= 50: return "silver"
        return "bronze"

class AppAPIDeveloperAPIApiDeveloperLeaderboard:
    def __init__(self) -> None:
        self._entries: dict[tuple[str, str], LeaderboardEntry] = {}

    def update(self, installation_id: str, developer_id: str, display_name: str, api_calls: int = 0, apps_created: int = 0, webhooks_configured: int = 0, docs_contributed: int = 0) -> LeaderboardEntry:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, developer_id)
        e = LeaderboardEntry(developer_id=developer_id, display_name=display_name, api_calls=api_calls, apps_created=apps_created, webhooks_configured=webhooks_configured, docs_contributed=docs_contributed)
        self._entries[key] = e
        return e

    def top(self, installation_id: str, limit: int = 10) -> list[LeaderboardEntry]:
        entries = [e for (inst, _), e in self._entries.items() if inst == installation_id]
        return sorted(entries, key=lambda e: e.total_score, reverse=True)[:limit]

    def tier_counts(self, installation_id: str) -> dict[str, int]:
        counts: dict[str, int] = {}
        for (inst, _), e in self._entries.items():
            if inst == installation_id:
                counts[e.rank_tier] = counts.get(e.rank_tier, 0) + 1
        return counts

    def get(self, installation_id: str, developer_id: str) -> LeaderboardEntry | None:
        return self._entries.get((installation_id, developer_id))
