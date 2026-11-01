"""App API Changelog Vote — upvote/downvote changelog entries."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class EntryVotes:
    entry_id: str
    upvotes: set[str] = field(default_factory=set)
    downvotes: set[str] = field(default_factory=set)

    @property
    def score(self) -> int:
        return len(self.upvotes) - len(self.downvotes)

class AppAPIChangelogVote:
    def __init__(self) -> None:
        self._votes: dict[tuple[str, str], EntryVotes] = {}

    def upvote(self, installation_id: str, entry_id: str, user_id: str) -> EntryVotes:
        if not installation_id: raise ValueError("installation_id is required")
        v = self._get_or_create(installation_id, entry_id)
        v.upvotes.add(user_id)
        v.downvotes.discard(user_id)  # can't have both
        return v

    def downvote(self, installation_id: str, entry_id: str, user_id: str) -> EntryVotes:
        if not installation_id: raise ValueError("installation_id is required")
        v = self._get_or_create(installation_id, entry_id)
        v.downvotes.add(user_id)
        v.upvotes.discard(user_id)
        return v

    def get_votes(self, installation_id: str, entry_id: str) -> EntryVotes:
        return self._get_or_create(installation_id, entry_id)

    def top_entries(self, installation_id: str, limit: int = 10) -> list[EntryVotes]:
        entries = [v for (inst, _), v in self._votes.items() if inst == installation_id]
        return sorted(entries, key=lambda v: v.score, reverse=True)[:limit]

    def _get_or_create(self, installation_id: str, entry_id: str) -> EntryVotes:
        key = (installation_id, entry_id)
        if key not in self._votes:
            self._votes[key] = EntryVotes(entry_id=entry_id)
        return self._votes[key]
