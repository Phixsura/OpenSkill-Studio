"""Migration assistant — guide users through breaking changes across versions."""


def detect_breaking_changes(*, old_manifest: dict, new_manifest: dict) -> list[dict]:
    changes = []
    old_scopes = set(old_manifest.get("scopes", []))
    new_scopes = set(new_manifest.get("scopes", []))
    removed_scopes = old_scopes - new_scopes
    for s in removed_scopes:
        changes.append({"type": "scope_removed", "detail": f"Scope '{s}' was removed", "severity": "high"})
    old_events = set(old_manifest.get("events", []))
    new_events = set(new_manifest.get("events", []))
    for e in old_events - new_events:
        changes.append({"type": "event_removed", "detail": f"Event '{e}' no longer supported", "severity": "medium"})
    if old_manifest.get("min_api_version") != new_manifest.get("min_api_version"):
        changes.append({"type": "api_version_change", "detail": "Minimum API version changed", "severity": "high"})
    return changes


def build_migration_guide(*, changes: list[dict], app_name: str) -> dict:
    steps = []
    for i, c in enumerate(changes):
        if c["type"] == "scope_removed":
            steps.append({"step": i + 1, "action": "Update permissions", "detail": c["detail"]})
        elif c["type"] == "event_removed":
            steps.append({"step": i + 1, "action": "Update event handlers", "detail": c["detail"]})
        elif c["type"] == "api_version_change":
            steps.append({"step": i + 1, "action": "Update API calls", "detail": c["detail"]})
    return {"app_name": app_name, "steps": steps, "total_steps": len(steps),
            "estimated_effort": "high" if any(c["severity"] == "high" for c in changes) else "low"}
