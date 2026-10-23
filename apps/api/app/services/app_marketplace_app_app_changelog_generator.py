"""Changelog generator — auto-generate changelog from git commits."""

import html
import re

CONVENTIONAL_RE = re.compile(r"^(feat|fix|docs|style|refactor|perf|test|chore|ci|build)(\(.+?\))?!?:\s+(.+)$")
TYPE_LABELS = {"feat": "Features", "fix": "Bug Fixes", "perf": "Performance",
               "docs": "Documentation", "refactor": "Refactoring", "chore": "Chores",
               "ci": "CI/CD", "build": "Build", "test": "Tests", "style": "Style"}
TYPE_ICONS = {"feat": "✨", "fix": "🐛", "perf": "⚡", "docs": "📝",
              "refactor": "♻️", "chore": "🔧", "ci": "🔄", "build": "📦"}


def parse_commits(*, commits: list[str]) -> dict:
    categorized: dict[str, list] = {}
    breaking = []
    unparsed = []
    for commit in commits:
        m = CONVENTIONAL_RE.match(commit.strip())
        if m:
            ctype, scope, desc = m.group(1), m.group(2), m.group(3)
            scope = scope.strip("()") if scope else None
            entry = {"type": ctype, "scope": scope, "description": html.escape(desc),
                     "icon": TYPE_ICONS.get(ctype, "📌")}
            categorized.setdefault(ctype, []).append(entry)
            if "!" in commit.split(":")[0]:
                breaking.append(html.escape(desc))
        else:
            unparsed.append(html.escape(commit.strip()))
    sections = [{"type": t, "label": TYPE_LABELS.get(t, t.title()),
                  "icon": TYPE_ICONS.get(t, "📌"), "entries": entries}
                 for t, entries in categorized.items()]
    return {"sections": sections, "total_commits": len(commits),
            "parsed": len(commits) - len(unparsed), "unparsed": unparsed,
            "breaking": breaking, "has_breaking": len(breaking) > 0}
