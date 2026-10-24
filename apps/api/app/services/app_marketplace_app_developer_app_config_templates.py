"""Config templates — predefined configuration presets for common use cases."""

TEMPLATES = {
    "minimal": {"timeout_ms": 3000, "retries": 1, "logging": "error", "cache_ttl": 0},
    "balanced": {"timeout_ms": 5000, "retries": 3, "logging": "warn", "cache_ttl": 300},
    "production": {"timeout_ms": 10000, "retries": 5, "logging": "info", "cache_ttl": 3600},
    "debug": {"timeout_ms": 30000, "retries": 0, "logging": "debug", "cache_ttl": 0},
}


def list_templates() -> list[dict]:
    return [{"id": k, "config": v, "field_count": len(v)} for k, v in TEMPLATES.items()]


def apply_template(*, template_id: str, overrides: dict | None = None) -> dict:
    if template_id not in TEMPLATES:
        return {"error": f"Unknown template: {template_id}"}
    config = dict(TEMPLATES[template_id])
    if overrides:
        config.update(overrides)
    return {"template": template_id, "config": config, "error": None}


def diff_with_template(*, current_config: dict, template_id: str) -> dict:
    template = TEMPLATES.get(template_id, {})
    diffs = []
    for key in set(list(current_config.keys()) + list(template.keys())):
        cur = current_config.get(key)
        tmpl = template.get(key)
        if cur != tmpl:
            diffs.append({"key": key, "current": cur, "template": tmpl})
    return {"template": template_id, "diffs": diffs, "diff_count": len(diffs),
            "matches_template": len(diffs) == 0}
