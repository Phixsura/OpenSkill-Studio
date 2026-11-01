"""Migration wizard — guide users through app-to-app migration."""


def analyze_migration(*, source_app: dict, target_app: dict) -> dict:
    source_scopes = set(source_app.get("scopes", []))
    target_scopes = set(target_app.get("scopes", []))
    source_events = set(source_app.get("event_types", []))
    target_events = set(target_app.get("event_types", []))
    return {
        "scope_overlap": sorted(source_scopes & target_scopes),
        "missing_scopes": sorted(source_scopes - target_scopes),
        "new_scopes": sorted(target_scopes - source_scopes),
        "event_overlap": sorted(source_events & target_events),
        "unmapped_events": sorted(source_events - target_events),
        "compatibility_score": round(
            len(source_scopes & target_scopes) / max(len(source_scopes), 1) * 100, 1),
    }


def build_migration_steps(*, analysis: dict, has_config: bool = True) -> list[dict]:
    steps = [{"step": 1, "action": "install_target", "title": "Install replacement app"}]
    if has_config:
        steps.append({"step": 2, "action": "migrate_config", "title": "Transfer configuration"})
    if analysis.get("new_scopes"):
        steps.append({"step": len(steps) + 1, "action": "grant_scopes", "title": "Grant new permissions"})
    steps.append({"step": len(steps) + 1, "action": "verify", "title": "Verify functionality"})
    steps.append({"step": len(steps) + 1, "action": "uninstall_source", "title": "Uninstall old app"})
    return steps
