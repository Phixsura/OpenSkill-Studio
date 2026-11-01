"""Version history — complete version history with diffs between versions."""


def build_version_history(*, versions: list[dict]) -> dict:
    history = []
    for i, v in enumerate(versions):
        entry = {"version": v["version"], "released_at": v.get("released_at", ""),
                  "change_count": len(v.get("changes", [])), "status": v.get("status", "published"),
                  "is_latest": i == 0, "has_breaking": v.get("has_breaking", False)}
        history.append(entry)
    return {"versions": history, "total": len(history),
            "latest_version": history[0]["version"] if history else None}


def get_version_diff_summary(*, from_version: dict, to_version: dict) -> dict:
    from_changes = len(from_version.get("changes", []))
    to_changes = len(to_version.get("changes", []))
    return {"from": from_version["version"], "to": to_version["version"],
            "changes_in_from": from_changes, "changes_in_to": to_changes,
            "net_changes": to_changes - from_changes}
