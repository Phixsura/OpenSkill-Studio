"""Changelog Generator — auto-generate changelogs from commit messages.

Parses conventional commit messages, groups by type, and produces
formatted changelogs for extension releases.
"""
from __future__ import annotations
import re
from dataclasses import dataclass, field


@dataclass
class CommitInfo:
    hash: str
    type: str  # feat, fix, chore, docs, etc.
    scope: str
    description: str
    breaking: bool = False
    body: str = ""


COMMIT_PATTERN = re.compile(
    r"^(?P<type>\w+)"
    r"(?:\((?P<scope>[^)]+)\))?"
    r"(?P<breaking>!)?"
    r":\s*(?P<desc>.+)$"
)

TYPE_LABELS = {
    "feat": "✨ Features",
    "fix": "🐛 Bug Fixes",
    "perf": "⚡ Performance",
    "docs": "📚 Documentation",
    "refactor": "♻️ Refactoring",
    "test": "🧪 Tests",
    "chore": "🔧 Chores",
    "ci": "🔄 CI/CD",
    "style": "💄 Style",
    "build": "📦 Build",
}

TYPE_ORDER = ["feat", "fix", "perf", "refactor", "docs", "test", "chore", "ci", "style", "build"]


def parse_commit(message: str, commit_hash: str = "") -> CommitInfo | None:
    """Parse a conventional commit message."""
    first_line = message.strip().split("\n")[0]
    m = COMMIT_PATTERN.match(first_line)
    if not m:
        return None
    body = "\n".join(message.strip().split("\n")[1:]).strip()
    return CommitInfo(
        hash=commit_hash, type=m.group("type"),
        scope=m.group("scope") or "",
        description=m.group("desc"),
        breaking=bool(m.group("breaking")) or "BREAKING CHANGE" in body,
        body=body,
    )


def generate_changelog(version: str, commits: list[CommitInfo],
                       date: str = "") -> str:
    """Generate a formatted changelog from parsed commits."""
    lines = [f"## {version}" + (f" ({date})" if date else ""), ""]

    # Breaking changes first
    breaking = [c for c in commits if c.breaking]
    if breaking:
        lines.append("### 🚨 Breaking Changes")
        lines.append("")
        for c in breaking:
            scope = f"**{c.scope}:** " if c.scope else ""
            lines.append(f"- {scope}{c.description}")
        lines.append("")

    # Group by type
    for commit_type in TYPE_ORDER:
        typed = [c for c in commits if c.type == commit_type and not c.breaking]
        if not typed:
            continue
        label = TYPE_LABELS.get(commit_type, commit_type.capitalize())
        lines.append(f"### {label}")
        lines.append("")
        for c in typed:
            scope = f"**{c.scope}:** " if c.scope else ""
            lines.append(f"- {scope}{c.description}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"
