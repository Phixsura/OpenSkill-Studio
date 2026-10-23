"""Release notes generator — auto-generate release notes from PRs."""
from __future__ import annotations
import html


def generate_notes(version: str, prs: list[dict], contributors: list[str]) -> dict:
    sections: dict[str, list[str]] = {}
    for pr in prs:
        label = pr.get("label", "other")
        title = html.escape(pr.get("title", ""))
        author = pr.get("author", "")
        sections.setdefault(label, []).append(f"{title} (@{author})")
    md_lines = [f"# Release {version}\n"]
    for section, items in sections.items():
        md_lines.append(f"\n## {section.title()}\n")
        for item in items:
            md_lines.append(f"- {item}")
    md_lines.append(f"\n---\nContributors: {', '.join(sorted(contributors))}")
    return {"version": version, "sections": sections, "pr_count": len(prs),
            "contributor_count": len(contributors),
            "markdown": "\n".join(md_lines)}


def diff_releases(prev_notes: dict, curr_notes: dict) -> dict:
    new_prs = curr_notes["pr_count"] - prev_notes["pr_count"]
    new_contributors = curr_notes["contributor_count"] - prev_notes["contributor_count"]
    return {"prev_version": prev_notes["version"], "curr_version": curr_notes["version"],
            "new_prs": new_prs, "new_contributors": new_contributors}
