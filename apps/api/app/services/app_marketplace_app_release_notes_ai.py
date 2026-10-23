"""Release notes AI — auto-generate release notes from commit messages and diffs."""


def categorize_commits(*, commits: list[dict]) -> dict:
    categories = {"features": [], "fixes": [], "improvements": [], "other": []}
    for c in commits:
        msg = c.get("message", "").lower()
        if msg.startswith("feat"):
            categories["features"].append(c)
        elif msg.startswith("fix"):
            categories["fixes"].append(c)
        elif msg.startswith(("refactor", "perf", "style", "chore")):
            categories["improvements"].append(c)
        else:
            categories["other"].append(c)
    return categories


def generate_release_notes(*, version: str, commits: list[dict], breaking: list[str] | None = None) -> dict:
    cats = categorize_commits(commits=commits)
    sections = []
    if breaking:
        sections.append({"title": "⚠️ Breaking Changes", "items": breaking})
    if cats["features"]:
        sections.append({"title": "✨ New Features", "items": [c["message"] for c in cats["features"]]})
    if cats["fixes"]:
        sections.append({"title": "🐛 Bug Fixes", "items": [c["message"] for c in cats["fixes"]]})
    if cats["improvements"]:
        sections.append({"title": "🔧 Improvements", "items": [c["message"] for c in cats["improvements"]]})
    return {"version": version, "sections": sections, "total_commits": len(commits)}


def render_release_notes_md(*, notes: dict) -> str:
    lines = [f"# Release {notes['version']}\n"]
    for section in notes["sections"]:
        lines.append(f"## {section['title']}\n")
        for item in section["items"]:
            lines.append(f"- {item}")
        lines.append("")
    lines.append(f"*{notes['total_commits']} commits in this release*")
    return "\n".join(lines)
