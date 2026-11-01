"""Changelog Generator — auto-generate changelogs from commit messages.

Parses conventional commits, groups by type (feat/fix/docs/chore),
generates markdown, and supports version tagging.
"""
from __future__ import annotations
import re
from collections import defaultdict
from dataclasses import dataclass, field


COMMIT_RE = re.compile(r"^(feat|fix|docs|chore|refactor|perf|test|ci|build|style)(?:\(([^)]+)\))?\!?:\s+(.+)$")
BREAKING_RE = re.compile(r"BREAKING\s*CHANGE|^.+!:")


@dataclass
class ParsedCommit:
    commit_type: str
    scope: str
    message: str
    is_breaking: bool


class ChangelogGenService:
    """Generates changelogs from conventional commits."""

    TYPE_LABELS = {
        "feat": "✨ Features", "fix": "🐛 Bug Fixes", "perf": "⚡ Performance",
        "docs": "📝 Documentation", "refactor": "♻️ Refactoring",
        "chore": "🔧 Chores", "ci": "🔄 CI", "test": "🧪 Tests",
        "build": "📦 Build", "style": "🎨 Style",
    }

    def parse_commits(self, messages: list[str]) -> list[ParsedCommit]:
        parsed = []
        for msg in messages:
            m = COMMIT_RE.match(msg.strip())
            if m:
                is_breaking = bool(BREAKING_RE.search(msg))
                parsed.append(ParsedCommit(
                    commit_type=m.group(1), scope=m.group(2) or "",
                    message=m.group(3), is_breaking=is_breaking,
                ))
        return parsed

    def generate(self, version: str, commits: list[str],
                 date: str = "") -> str:
        parsed = self.parse_commits(commits)
        if not parsed:
            return f"## {version}\n\nNo conventional commits found.\n"

        grouped: dict[str, list[ParsedCommit]] = defaultdict(list)
        for c in parsed:
            grouped[c.commit_type].append(c)

        lines = [f"## {version}" + (f" ({date})" if date else ""), ""]

        # Breaking changes first
        breaking = [c for c in parsed if c.is_breaking]
        if breaking:
            lines.append("### ⚠️ Breaking Changes")
            for c in breaking:
                lines.append(f"- {c.message}")
            lines.append("")

        for ctype in ["feat", "fix", "perf", "refactor", "docs", "chore", "ci", "test", "build", "style"]:
            entries = grouped.get(ctype, [])
            non_breaking = [c for c in entries if not c.is_breaking]
            if non_breaking:
                lines.append(f"### {self.TYPE_LABELS.get(ctype, ctype)}")
                for c in non_breaking:
                    scope = f"**{c.scope}:** " if c.scope else ""
                    lines.append(f"- {scope}{c.message}")
                lines.append("")

        return "\n".join(lines)

    def get_stats(self, commits: list[str]) -> dict:
        parsed = self.parse_commits(commits)
        by_type: dict[str, int] = defaultdict(int)
        for c in parsed:
            by_type[c.commit_type] += 1
        return {
            "total": len(commits), "conventional": len(parsed),
            "breaking": sum(1 for c in parsed if c.is_breaking),
            "by_type": dict(by_type),
        }
