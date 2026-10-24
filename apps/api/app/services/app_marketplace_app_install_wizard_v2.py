"""Install wizard v2 — guided multi-step install with permission review."""


def build_install_wizard(*, app: dict, required_scopes: list[str],
                            optional_scopes: list[str], config_fields: list[dict]) -> dict:
    steps = [
        {"key": "permissions", "title": "Review Permissions", "required_scopes": required_scopes, "optional_scopes": optional_scopes},
        {"key": "configure", "title": "Configure", "fields": config_fields},
        {"key": "confirm", "title": "Confirm & Install"},
    ]
    return {"app_name": app["name"], "steps": steps, "step_count": len(steps),
            "has_config": len(config_fields) > 0, "total_scopes": len(required_scopes) + len(optional_scopes)}


def validate_install_config(*, config: dict, required_fields: list[str]) -> dict:
    missing = [f for f in required_fields if f not in config or not config[f]]
    return {"valid": len(missing) == 0, "missing_fields": missing}
