"""App API Changelog Digest — compile periodic changelog digests.

Manages changelog digests:
- Compile entries into periodic digests (daily/weekly/monthly)
- Track digest generation and delivery
- Per-installation scoped digests
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class DigestEntry:
    """An entry in a digest."""

    title: str
    version: str
    category: str


@dataclass
class ChangelogDigest:
    """A compiled changelog digest."""

    digest_id: str
    period: str  # "daily", "weekly", "monthly"
    period_label: str  # "2024-01-15" or "2024-W03"
    entries: list[DigestEntry] = field(default_factory=list)
    delivered: bool = False
    created_at: float = field(default_factory=time.time)

    @property
    def entry_count(self) -> int:
        return len(self.entries)


class AppAPIChangelogDigest:
    """Compile periodic changelog digests."""

    def __init__(self) -> None:
        self._digests: dict[tuple[str, str], ChangelogDigest] = {}

    def compile(
        self, installation_id: str, digest_id: str, period: str,
        period_label: str, entries: list[dict],
    ) -> ChangelogDigest:
        if not installation_id:
            raise ValueError("installation_id is required")
        if period not in ("daily", "weekly", "monthly"):
            raise ValueError("period must be daily, weekly, or monthly")

        entry_objs = [DigestEntry(title=e["title"], version=e["version"], category=e.get("category", "general")) for e in entries]
        digest = ChangelogDigest(
            digest_id=digest_id, period=period,
            period_label=period_label, entries=entry_objs,
        )
        self._digests[(installation_id, digest_id)] = digest
        return digest

    def mark_delivered(self, installation_id: str, digest_id: str) -> ChangelogDigest:
        d = self._get(installation_id, digest_id)
        d.delivered = True
        return d

    def list_digests(self, installation_id: str, period: str | None = None) -> list[ChangelogDigest]:
        digests = [d for (inst, _), d in self._digests.items() if inst == installation_id]
        if period:
            digests = [d for d in digests if d.period == period]
        return digests

    def _get(self, installation_id: str, digest_id: str) -> ChangelogDigest:
        key = (installation_id, digest_id)
        d = self._digests.get(key)
        if d is None:
            raise KeyError(f"Digest {digest_id} not found")
        return d
