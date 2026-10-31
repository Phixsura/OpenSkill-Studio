"""Webhook templates — predefined payloads for common event types."""

WEBHOOK_TEMPLATES = {
    "app.installed": {
        "event": "app.installed",
        "payload": {"installation_id": "{{installation_id}}", "org_id": "{{org_id}}",
                     "app_id": "{{app_id}}", "installed_by": "{{user_id}}"},
    },
    "app.uninstalled": {
        "event": "app.uninstalled",
        "payload": {"installation_id": "{{installation_id}}", "org_id": "{{org_id}}"},
    },
    "version.published": {
        "event": "version.published",
        "payload": {"app_id": "{{app_id}}", "version": "{{version}}", "changelog": "{{changelog}}"},
    },
    "review.created": {
        "event": "review.created",
        "payload": {"app_id": "{{app_id}}", "rating": "{{rating}}", "reviewer_id": "{{reviewer_id}}"},
    },
}


def get_template(event_type: str) -> dict | None:
    return WEBHOOK_TEMPLATES.get(event_type)


def list_templates() -> list[dict]:
    return [{"event": k, "fields": list(v["payload"].keys())} for k, v in WEBHOOK_TEMPLATES.items()]


def render_template(*, event_type: str, values: dict) -> dict | None:
    tmpl = WEBHOOK_TEMPLATES.get(event_type)
    if not tmpl:
        return None
    payload = {}
    for k, v in tmpl["payload"].items():
        if isinstance(v, str) and v.startswith("{{") and v.endswith("}}"):
            key = v[2:-2]
            payload[k] = values.get(key, v)
        else:
            payload[k] = v
    return {"event": event_type, "payload": payload}
