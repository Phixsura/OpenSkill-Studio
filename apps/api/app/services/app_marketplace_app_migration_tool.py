"""App migration tool — help developers migrate between app versions."""


def plan_migration(*, from_version: str, to_version: str,
                     breaking_changes: list[dict]) -> dict:
    steps = []
    for i, bc in enumerate(breaking_changes, 1):
        steps.append({
            "step": i,
            "type": bc.get("type", "code_change"),
            "description": bc["description"],
            "automated": bc.get("automated", False),
            "risk": bc.get("risk", "low"),
        })
    auto_count = sum(1 for s in steps if s["automated"])
    return {
        "from_version": from_version,
        "to_version": to_version,
        "total_steps": len(steps),
        "automated_steps": auto_count,
        "manual_steps": len(steps) - auto_count,
        "steps": steps,
        "estimated_time_min": len(steps) * 15,
        "can_auto_migrate": auto_count == len(steps),
    }


def run_migration_check(*, app_id: str, target_version: str) -> dict:
    checks = [
        {"name": "API compatibility", "status": "pass", "details": "All endpoints compatible"},
        {"name": "Schema migration", "status": "pass", "details": "No breaking schema changes"},
        {"name": "Dependency check", "status": "warning", "details": "2 deps need update"},
        {"name": "Permission scope", "status": "pass", "details": "No new permissions required"},
    ]
    all_pass = all(c["status"] == "pass" for c in checks)
    return {"app_id": app_id, "target_version": target_version,
            "checks": checks, "ready": all_pass,
            "warnings": sum(1 for c in checks if c["status"] == "warning")}
