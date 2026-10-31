"""App changelog timeline — visual timeline of all app versions."""


def build_changelog_timeline(*, versions: list[dict]) -> dict:
    timeline = []
    for v in versions:
        changes = v.get("changes", [])
        features = sum(1 for c in changes if c.get("type") == "feature")
        fixes = sum(1 for c in changes if c.get("type") == "fix")
        breaking = sum(1 for c in changes if c.get("breaking"))
        timeline.append({
            "version": v["version"],
            "date": v.get("date", ""),
            "title": v.get("title", f"v{v['version']}"),
            "features": features,
            "fixes": fixes,
            "breaking": breaking,
            "total_changes": len(changes),
            "is_major": v["version"].endswith(".0.0") or v["version"].startswith(v["version"].split(".")[0] + ".0.0"),
        })
    return {"timeline": timeline, "total_versions": len(timeline),
            "total_changes": sum(t["total_changes"] for t in timeline)}
