"""Release notes AI — generate human-readable release notes from commits."""

import re


def generate_release_notes(*, version: str, commits: list[str],
                             app_name: str) -> dict:
    sections: dict[str, list[str]] = {}
    for msg in commits:
        m = re.match(r"^(\w+)(?:\(.+?\))?!?:\s*(.+)$", msg)
        if m:
            prefix, desc = m.group(1), m.group(2).strip()
            if prefix in ("feat", "feature"):
                sections.setdefault("🚀 New Features", []).append(desc)
            elif prefix == "fix":
                sections.setdefault("🐛 Bug Fixes", []).append(desc)
            elif prefix == "perf":
                sections.setdefault("⚡ Performance", []).append(desc)
            elif prefix in ("docs", "doc"):
                sections.setdefault("📚 Documentation", []).append(desc)
            elif prefix in ("refactor", "chore", "ci", "build", "style", "test"):
                sections.setdefault("🔧 Maintenance", []).append(desc)
            else:
                sections.setdefault("📋 Other", []).append(desc)
        else:
            sections.setdefault("📋 Other", []).append(msg.strip())

    lines = [f"# {app_name} v{version}\n"]
    for section, items in sections.items():
        lines.append(f"\n## {section}\n")
        for item in items:
            lines.append(f"- {item}")
    markdown = "\n".join(lines)
    return {
        "version": version,
        "markdown": markdown,
        "section_count": len(sections),
        "commit_count": len(commits),
        "has_features": "🚀 New Features" in sections,
        "has_fixes": "🐛 Bug Fixes" in sections,
    }
