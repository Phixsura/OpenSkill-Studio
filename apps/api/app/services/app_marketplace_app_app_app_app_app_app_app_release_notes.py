"""Release notes generator — compile commits into structured release notes."""
from __future__ import annotations
import re

COMMIT_RE = re.compile(r"^(feat|fix|docs|chore|refactor|perf|test|ci|style)(?:\(([^)]+)\))?:\s*(.+)")
CATEGORY_LABEL = {
    "feat": "✨ New Features", "fix": "🐛 Bug Fixes", "perf": "⚡ Performance",
    "docs": "📝 Documentation", "refactor": "♻️ Refactoring", "chore": "🔧 Chores",
    "test": "🧪 Tests", "ci": "🔄 CI/CD", "style": "💅 Style",
}


def generate_release_notes(commits: list[str], *, version: str, date: str = "") -> dict:
    sections: dict[str, list[dict]] = {}
    uncategorized = []
    for commit in commits:
        m = COMMIT_RE.match(commit)
        if m:
            cat, scope, msg = m.group(1), m.group(2) or "", m.group(3)
            sections.setdefault(cat, []).append({"scope": scope, "message": msg})
        else:
            uncategorized.append(commit)
    output = []
    for cat in ("feat", "fix", "perf", "docs", "refactor", "chore", "test", "ci", "style"):
        if cat in sections:
            output.append({"category": cat, "label": CATEGORY_LABEL[cat],
                           "items": sections[cat], "count": len(sections[cat])})
    breaking = [c for c in commits if "BREAKING" in c.upper()]
    return {
        "version": version, "date": date,
        "total_commits": len(commits),
        "sections": output,
        "uncategorized": uncategorized,
        "has_breaking": len(breaking) > 0,
        "breaking_count": len(breaking),
    }
