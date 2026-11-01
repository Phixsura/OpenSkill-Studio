"""Changelog AI v2 — intelligent changelog with audience-specific messaging."""


def generate_user_changelog(*, changes: list[dict], audience: str = "end_user") -> dict:
    templates = {
        "end_user": {"prefix": "What's new:", "skip_types": ["chore", "refactor", "test"]},
        "developer": {"prefix": "Technical changelog:", "skip_types": []},
        "admin": {"prefix": "Admin update:", "skip_types": ["test"]},
    }
    config = templates.get(audience, templates["end_user"])
    filtered = [c for c in changes if c.get("type") not in config["skip_types"]]
    entries = []
    for c in filtered:
        if audience == "end_user":
            entries.append(c.get("user_facing_description", c.get("description", "")))
        else:
            entries.append(f"[{c.get('type', 'misc')}] {c.get('description', '')}")
    return {"audience": audience, "prefix": config["prefix"], "entries": entries, "count": len(entries)}


def summarize_changelog(*, changes: list[dict]) -> dict:
    by_type = {}
    for c in changes:
        t = c.get("type", "other")
        by_type.setdefault(t, []).append(c)
    headline_parts = []
    if "feat" in by_type:
        headline_parts.append(f"{len(by_type['feat'])} new features")
    if "fix" in by_type:
        headline_parts.append(f"{len(by_type['fix'])} bug fixes")
    if "perf" in by_type:
        headline_parts.append(f"{len(by_type['perf'])} performance improvements")
    return {"headline": ", ".join(headline_parts) or "Maintenance update",
            "total_changes": len(changes), "by_type": {k: len(v) for k, v in by_type.items()}}
