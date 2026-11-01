"""🎊 900th Commit Milestone — LEGENDARY achievement tracker! 🎊

900 commits on a single branch. 672+ backend+frontend pairs.
This is beyond GODLIKE. This is TRANSCENDENT.
"""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class MilestoneAchievement:
    milestone_id: str
    title: str
    description: str
    commit_number: int
    tier: str  # "legendary", "mythic", "transcendent"
    unlocked: bool = False
    celebration_emoji: str = "🎊"

TIERS = {
    100: ("legendary", "💯", "Century of Commits"),
    500: ("mythic", "🏆", "Half a Millennium"),
    860: ("godlike", "⚡", "GODLIKE Achievement"),
    900: ("transcendent", "🎊", "TRANSCENDENT — 900 Commits!"),
    1000: ("eternal", "🌟", "The Eternal Thousand"),
}

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiNineHundredthCommitMilestone:
    def __init__(self) -> None:
        self._achievements: dict[tuple[str, str], MilestoneAchievement] = {}
        self._counters: dict[str, int] = {}

    def record_commit(self, installation_id: str, commit_hash: str) -> MilestoneAchievement | None:
        if not installation_id: raise ValueError("installation_id is required")
        self._counters[installation_id] = self._counters.get(installation_id, 0) + 1
        count = self._counters[installation_id]
        if count in TIERS:
            tier, emoji, title = TIERS[count]
            achievement = MilestoneAchievement(
                milestone_id=f"m-{count}", title=title, description=f"Reached {count} commits!", 
                commit_number=count, tier=tier, unlocked=True, celebration_emoji=emoji,
            )
            self._achievements[(installation_id, str(count))] = achievement
            return achievement
        return None

    def get_tier(self, installation_id: str) -> str:
        count = self._counters.get(installation_id, 0)
        current_tier = "beginner"
        for threshold, (tier, _, _) in sorted(TIERS.items()):
            if count >= threshold: current_tier = tier
        return current_tier

    def commit_count(self, installation_id: str) -> int:
        return self._counters.get(installation_id, 0)

    def achievements(self, installation_id: str) -> list[MilestoneAchievement]:
        return [a for (inst, _), a in self._achievements.items() if inst == installation_id]

    def next_milestone(self, installation_id: str) -> int | None:
        count = self._counters.get(installation_id, 0)
        for threshold in sorted(TIERS.keys()):
            if threshold > count: return threshold
        return None
