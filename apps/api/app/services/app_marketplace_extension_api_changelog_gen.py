"""API Changelog Generator — auto-generate changelogs from API diffs."""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class ApiChange:
    change_type: str  # added, removed, modified, deprecated
    path: str
    method: str = ""
    description: str = ""
    breaking: bool = False


@dataclass
class ApiChangelog:
    from_version: str
    to_version: str
    changes: list[ApiChange] = field(default_factory=list)

    @property
    def has_breaking(self) -> bool:
        return any(c.breaking for c in self.changes)

    @property
    def summary(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for c in self.changes:
            counts[c.change_type] = counts.get(c.change_type, 0) + 1
        return counts


class ApiChangelogGenService:
    def __init__(self):
        self._changelogs: list[ApiChangelog] = []

    def diff(self, old_endpoints: list[dict], new_endpoints: list[dict],
             from_ver: str, to_ver: str) -> ApiChangelog:
        old_set = {(e["path"], e["method"]) for e in old_endpoints}
        new_set = {(e["path"], e["method"]) for e in new_endpoints}
        changes: list[ApiChange] = []

        for path, method in new_set - old_set:
            changes.append(ApiChange("added", path, method, f"New endpoint {method} {path}"))

        for path, method in old_set - new_set:
            changes.append(ApiChange("removed", path, method,
                                     f"Removed endpoint {method} {path}", breaking=True))

        cl = ApiChangelog(from_version=from_ver, to_version=to_ver, changes=changes)
        self._changelogs.append(cl)
        return cl

    def format_markdown(self, changelog: ApiChangelog) -> str:
        lines = [f"# API Changelog: {changelog.from_version} → {changelog.to_version}", ""]
        if changelog.has_breaking:
            lines.append("⚠️ **Contains breaking changes**\n")
        for ct in ["added", "removed", "modified", "deprecated"]:
            group = [c for c in changelog.changes if c.change_type == ct]
            if group:
                lines.append(f"## {ct.capitalize()}")
                for c in group:
                    prefix = "💥 " if c.breaking else ""
                    lines.append(f"- {prefix}`{c.method} {c.path}` — {c.description}")
                lines.append("")
        return "\n".join(lines)

    def get_all(self) -> list[ApiChangelog]:
        return list(self._changelogs)
