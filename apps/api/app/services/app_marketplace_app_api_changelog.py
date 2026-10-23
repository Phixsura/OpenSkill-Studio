"""API changelog — track and display API changes between versions."""


CHANGE_TYPES = {
    "added": {"label": "Added", "icon": "➕", "breaking": False},
    "changed": {"label": "Changed", "icon": "🔄", "breaking": False},
    "deprecated": {"label": "Deprecated", "icon": "⚠️", "breaking": False},
    "removed": {"label": "Removed", "icon": "❌", "breaking": True},
    "fixed": {"label": "Fixed", "icon": "🐛", "breaking": False},
    "security": {"label": "Security", "icon": "🔒", "breaking": False},
}


def build_api_changelog(*, version: str, changes: list[dict]) -> dict:
    grouped: dict[str, list] = {}
    breaking = []
    for change in changes:
        ctype = change.get("type", "changed")
        info = CHANGE_TYPES.get(ctype, CHANGE_TYPES["changed"])
        entry = {"endpoint": change.get("endpoint", ""),
                 "description": change.get("description", ""), **info}
        grouped.setdefault(ctype, []).append(entry)
        if info["breaking"] or change.get("breaking"):
            breaking.append(entry)
    sections = [{"type": k, "label": CHANGE_TYPES.get(k, {}).get("label", k),
                  "icon": CHANGE_TYPES.get(k, {}).get("icon", ""),
                  "entries": v} for k, v in grouped.items()]
    return {
        "version": version,
        "sections": sections,
        "total_changes": len(changes),
        "breaking_changes": breaking,
        "has_breaking": len(breaking) > 0,
    }
