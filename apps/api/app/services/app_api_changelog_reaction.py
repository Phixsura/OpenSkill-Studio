"""App API Changelog Reaction — collect reactions on changelog entries.

Manages changelog reactions:
- Add emoji reactions to entries
- Track reaction counts
- Per-installation scoped reactions
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()

ALLOWED_REACTIONS = {"👍", "👎", "🎉", "❤️", "🚀", "👀"}


@dataclass
class EntryReactions:
    """Reactions on a changelog entry."""

    entry_id: str
    reactions: dict[str, set[str]] = field(default_factory=dict)  # emoji → user_ids

    @property
    def total(self) -> int:
        return sum(len(users) for users in self.reactions.values())

    def counts(self) -> dict[str, int]:
        return {emoji: len(users) for emoji, users in self.reactions.items() if users}


class AppAPIChangelogReaction:
    """Collect reactions on changelog entries."""

    def __init__(self) -> None:
        self._entries: dict[tuple[str, str], EntryReactions] = {}

    def react(
        self, installation_id: str, entry_id: str, user_id: str, emoji: str,
    ) -> EntryReactions:
        if not installation_id:
            raise ValueError("installation_id is required")
        if emoji not in ALLOWED_REACTIONS:
            raise ValueError(f"emoji must be one of {ALLOWED_REACTIONS}")

        key = (installation_id, entry_id)
        if key not in self._entries:
            self._entries[key] = EntryReactions(entry_id=entry_id)

        entry = self._entries[key]
        entry.reactions.setdefault(emoji, set()).add(user_id)
        return entry

    def unreact(
        self, installation_id: str, entry_id: str, user_id: str, emoji: str,
    ) -> EntryReactions:
        key = (installation_id, entry_id)
        entry = self._entries.get(key)
        if entry is None:
            raise KeyError(f"Entry {entry_id} not found")
        if emoji in entry.reactions:
            entry.reactions[emoji].discard(user_id)
        return entry

    def get_reactions(self, installation_id: str, entry_id: str) -> EntryReactions:
        key = (installation_id, entry_id)
        return self._entries.get(key, EntryReactions(entry_id=entry_id))
