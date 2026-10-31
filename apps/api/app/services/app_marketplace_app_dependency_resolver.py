"""Dependency resolver — resolve and validate app dependency trees."""


def resolve_dependencies(*, app: dict, available: dict[str, dict]) -> dict:
    resolved = []
    unresolved = []
    visited = set()

    def _resolve(app_id: str) -> None:
        if app_id in visited:
            return
        visited.add(app_id)
        dep = available.get(app_id)
        if not dep:
            unresolved.append(app_id)
            return
        for child_id in dep.get("depends_on", []):
            _resolve(child_id)
        resolved.append(app_id)

    for dep_id in app.get("depends_on", []):
        _resolve(dep_id)

    return {"resolved": resolved, "unresolved": unresolved,
            "install_order": resolved, "can_install": len(unresolved) == 0}


def check_version_compatibility(*, required: dict[str, str], installed: dict[str, str]) -> dict:
    incompatible = []
    missing = []
    for dep_id, req_version in required.items():
        inst_version = installed.get(dep_id)
        if not inst_version:
            missing.append(dep_id)
        elif inst_version < req_version:
            incompatible.append({"id": dep_id, "required": req_version, "installed": inst_version})
    return {"compatible": not incompatible and not missing,
            "incompatible": incompatible, "missing": missing}
