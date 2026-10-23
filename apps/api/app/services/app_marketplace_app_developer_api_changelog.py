"""Developer API changelog — track API changes across versions."""

def build_api_changelog(*, versions: list[dict]) -> list[dict]:
    entries = []
    for v in versions:
        added = v.get("endpoints_added", [])
        removed = v.get("endpoints_removed", [])
        modified = v.get("endpoints_modified", [])
        if added or removed or modified:
            entries.append({"version": v["version"], "added": len(added),
                            "removed": len(removed), "modified": len(modified),
                            "breaking": len(removed) > 0})
    return entries

def compute_api_stability(*, changelog: list[dict]) -> dict:
    if not changelog:
        return {"stability_score": 100, "breaking_changes": 0}
    breaking = sum(1 for e in changelog if e.get("breaking"))
    return {"stability_score": round(max(0, 100 - breaking * 15), 1), "breaking_changes": breaking,
            "total_versions": len(changelog)}
