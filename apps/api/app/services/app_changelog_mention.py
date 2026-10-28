"""App Changelog Mention — track @mentions and references in changelogs.

Extracts and indexes mentions from changelog entries:
- Parse @user, #issue, and PR references from text
- Index mentions per release
- Query releases mentioning a user or issue
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()

_USER_RE = re.compile(r"@([a-zA-Z0-9_-]+)")
_ISSUE_RE = re.compile(r"(?<!PR\s)(?<!PR)#(\d+)")
_PR_RE = re.compile(r"PR[- ]?#?(\d+)", re.IGNORECASE)


@dataclass
class MentionIndex:
    """Mentions extracted from a release."""

    version: str
    users: list[str] = field(default_factory=list)
    issues: list[int] = field(default_factory=list)
    prs: list[int] = field(default_factory=list)


class AppChangelogMention:
    """Track @mentions and references in changelogs."""

    def __init__(self) -> None:
        # (installation_id, version) → MentionIndex
        self._index: dict[tuple[str, str], MentionIndex] = {}

    def extract_and_index(
        self,
        installation_id: str,
        version: str,
        text: str,
    ) -> MentionIndex:
        """Extract mentions from text and index them."""
        if not installation_id:
            raise ValueError("installation_id is required")
        if not version:
            raise ValueError("version is required")

        users = sorted(set(_USER_RE.findall(text)))
        issues = sorted(set(int(m) for m in _ISSUE_RE.findall(text)))
        prs = sorted(set(int(m) for m in _PR_RE.findall(text)))

        index = MentionIndex(version=version, users=users, issues=issues, prs=prs)
        self._index[(installation_id, version)] = index
        return index

    def get_mentions(self, installation_id: str, version: str) -> MentionIndex:
        key = (installation_id, version)
        idx = self._index.get(key)
        if idx is None:
            raise KeyError(f"No mentions indexed for version {version}")
        return idx

    def find_by_user(self, installation_id: str, user: str) -> list[str]:
        """Find all versions mentioning a user."""
        return sorted(
            idx.version for (inst, _), idx in self._index.items()
            if inst == installation_id and user in idx.users
        )

    def find_by_issue(self, installation_id: str, issue_number: int) -> list[str]:
        """Find all versions referencing an issue."""
        return sorted(
            idx.version for (inst, _), idx in self._index.items()
            if inst == installation_id and issue_number in idx.issues
        )

    def find_by_pr(self, installation_id: str, pr_number: int) -> list[str]:
        """Find all versions referencing a PR."""
        return sorted(
            idx.version for (inst, _), idx in self._index.items()
            if inst == installation_id and pr_number in idx.prs
        )

    def all_mentioned_users(self, installation_id: str) -> list[str]:
        """Get all mentioned users across all versions."""
        users: set[str] = set()
        for (inst, _), idx in self._index.items():
            if inst == installation_id:
                users.update(idx.users)
        return sorted(users)
