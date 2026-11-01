"""API Changelog Generator — auto-generate changelogs from API version diffs."""
from __future__ import annotations
from dataclasses import dataclass, field
from xml.sax.saxutils import escape
import structlog

log = structlog.get_logger()

@dataclass
class ChangeEntry:
    change_id: str
    version: str
    change_type: str  # "added", "changed", "deprecated", "removed", "fixed", "security"
    description: str
    endpoints: list[str] = field(default_factory=list)
    breaking: bool = False

VALID_TYPES = {"added", "changed", "deprecated", "removed", "fixed", "security"}

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiChangelogGenerator:
    def __init__(self) -> None:
        self._entries: dict[tuple[str, str], list[ChangeEntry]] = {}

    def add_entry(self, installation_id: str, entry: ChangeEntry) -> ChangeEntry:
        if not installation_id: raise ValueError("installation_id is required")
        if entry.change_type not in VALID_TYPES: raise ValueError(f"Invalid type: {entry.change_type}")
        self._entries.setdefault((installation_id, entry.version), []).append(entry)
        return entry

    def generate_markdown(self, installation_id: str, version: str) -> str:
        entries = self._entries.get((installation_id, version), [])
        if not entries: return f"# {version}\n\nNo changes recorded."
        lines = [f"# {version}\n"]
        grouped: dict[str, list[ChangeEntry]] = {}
        for e in entries: grouped.setdefault(e.change_type, []).append(e)
        type_order = ["added", "changed", "deprecated", "removed", "fixed", "security"]
        type_emoji = {"added": "✨", "changed": "🔄", "deprecated": "⚠️", "removed": "🗑️", "fixed": "🐛", "security": "🔒"}
        for t in type_order:
            if t not in grouped: continue
            lines.append(f"\n## {type_emoji.get(t, '')} {t.capitalize()}\n")
            for e in grouped[t]:
                prefix = "**BREAKING** " if e.breaking else ""
                lines.append(f"- {prefix}{e.description}")
                if e.endpoints: lines.append(f"  - Endpoints: {', '.join(e.endpoints)}")
        return "\n".join(lines)

    def generate_rss_item(self, installation_id: str, version: str) -> str:
        entries = self._entries.get((installation_id, version), [])
        descs = [escape(e.description) for e in entries]
        return f"<item><title>{escape(version)}</title><description>{'; '.join(descs)}</description></item>"

    def breaking_changes(self, installation_id: str, version: str | None = None) -> list[ChangeEntry]:
        result: list[ChangeEntry] = []
        for (inst, v), entries in self._entries.items():
            if inst != installation_id: continue
            if version and v != version: continue
            result.extend(e for e in entries if e.breaking)
        return result

    def versions(self, installation_id: str) -> list[str]:
        return list(dict.fromkeys(v for (inst, v) in self._entries if inst == installation_id))
