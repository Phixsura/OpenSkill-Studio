"""App API Developer API Changelog Generator — auto-generate changelogs from diffs."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class ChangelogEntry:
    entry_id: str
    version: str
    category: str  # "added", "changed", "deprecated", "removed", "fixed", "security"
    description: str
    breaking: bool = False
    created_at: float = field(default_factory=time.time)

@dataclass
class Changelog:
    version: str
    entries: list[ChangelogEntry] = field(default_factory=list)
    published: bool = False

    @property
    def breaking_count(self) -> int:
        return sum(1 for e in self.entries if e.breaking)

class AppAPIDeveloperAPIApiChangelogGenerator:
    def __init__(self) -> None:
        self._changelogs: dict[tuple[str, str], Changelog] = {}

    def create(self, installation_id: str, version: str) -> Changelog:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, version)
        if key in self._changelogs: raise ValueError(f"Changelog for {version} exists")
        c = Changelog(version=version)
        self._changelogs[key] = c
        return c

    def add_entry(self, installation_id: str, version: str, entry_id: str, category: str, description: str, breaking: bool = False) -> ChangelogEntry:
        valid = {"added", "changed", "deprecated", "removed", "fixed", "security"}
        if category not in valid: raise ValueError(f"Invalid category: {category}")
        key = (installation_id, version)
        c = self._changelogs.get(key)
        if c is None: raise KeyError(f"No changelog for {version}")
        if c.published: raise ValueError("Cannot modify published changelog")
        e = ChangelogEntry(entry_id=entry_id, version=version, category=category, description=description, breaking=breaking)
        c.entries.append(e)
        return e

    def publish(self, installation_id: str, version: str) -> Changelog:
        key = (installation_id, version)
        c = self._changelogs.get(key)
        if c is None: raise KeyError(f"No changelog for {version}")
        c.published = True
        return c

    def list_changelogs(self, installation_id: str) -> list[Changelog]:
        return [c for (inst, _), c in self._changelogs.items() if inst == installation_id]

    def render_markdown(self, installation_id: str, version: str) -> str:
        key = (installation_id, version)
        c = self._changelogs.get(key)
        if c is None: raise KeyError(f"No changelog for {version}")
        lines = [f"## {version}"]
        by_cat: dict[str, list[ChangelogEntry]] = {}
        for e in c.entries:
            by_cat.setdefault(e.category, []).append(e)
        for cat in ["added", "changed", "deprecated", "removed", "fixed", "security"]:
            if cat in by_cat:
                lines.append(f"\n### {cat.title()}")
                for e in by_cat[cat]:
                    prefix = "**BREAKING:** " if e.breaking else ""
                    lines.append(f"- {prefix}{e.description}")
        return "\n".join(lines)
