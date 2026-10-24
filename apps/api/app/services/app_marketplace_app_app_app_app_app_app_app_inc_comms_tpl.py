"""Incident communication template — generate stakeholder communications."""
from __future__ import annotations
import html

TEMPLATES = {
    "investigating": "We are currently investigating {service}. Impact: {impact}. We will provide updates.",
    "identified": "The issue with {service} has been identified. Root cause: {cause}. Working on fix.",
    "monitoring": "{service} fix has been deployed. We are monitoring for stability.",
    "resolved": "{service} incident is resolved. Duration: {duration}. Root cause: {cause}.",
}


def generate_comms(template_type: str, context: dict) -> dict:
    template = TEMPLATES.get(template_type)
    if not template:
        return {"generated": False, "error": "unknown_template"}
    safe_context = {k: html.escape(str(v)) for k, v in context.items()}
    try:
        message = template.format(**safe_context)
    except KeyError:
        message = template
    return {"generated": True, "type": template_type, "message": message,
            "audience": "stakeholders", "channels": ["email", "status_page", "slack"]}


def comms_history(messages: list[dict]) -> dict:
    by_type: dict[str, int] = {}
    for m in messages:
        by_type[m.get("type", "")] = by_type.get(m.get("type", ""), 0) + 1
    return {"total": len(messages), "by_type": by_type}
