"""Release notes builder — compile release notes from version data."""


def build_release_notes(*, version: str, changelog: str | None, diff_summary: str | None,
                          breaking: bool, new_permissions: list[str]) -> dict:
    sections = []
    if breaking:
        sections.append({"type": "breaking", "content": "⚠️ This is a breaking change"})
    if new_permissions:
        sections.append({"type": "permissions", "content": f"New permissions: {', '.join(new_permissions)}"})
    if changelog:
        sections.append({"type": "notes", "content": changelog})
    if diff_summary:
        sections.append({"type": "diff", "content": diff_summary})
    if not sections:
        sections.append({"type": "notes", "content": "Minor updates and improvements"})
    return {"version": version, "sections": sections, "breaking": breaking}
