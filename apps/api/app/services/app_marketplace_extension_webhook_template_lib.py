"""Webhook Template Library — pre-built webhook payload templates."""
from __future__ import annotations
from dataclasses import dataclass, field
import json


@dataclass
class WebhookTemplate:
    template_id: str
    name: str
    event_type: str
    payload_schema: dict
    description: str = ""
    example_payload: dict = field(default_factory=dict)


class WebhookTemplateLibService:
    def __init__(self):
        self._templates: dict[str, WebhookTemplate] = {}
        self._seed_defaults()

    def _seed_defaults(self):
        defaults = [
            ("install", "Extension Installed", "extension.installed",
             {"extension_id": "string", "user_id": "string", "installed_at": "timestamp"}),
            ("uninstall", "Extension Uninstalled", "extension.uninstalled",
             {"extension_id": "string", "user_id": "string", "reason": "string"}),
            ("review", "New Review", "extension.review.created",
             {"extension_id": "string", "rating": "number", "comment": "string"}),
            ("update", "Extension Updated", "extension.updated",
             {"extension_id": "string", "old_version": "string", "new_version": "string"}),
        ]
        for tid, name, evt, schema in defaults:
            self._templates[tid] = WebhookTemplate(
                template_id=tid, name=name, event_type=evt, payload_schema=schema)

    def get(self, template_id: str) -> WebhookTemplate | None:
        return self._templates.get(template_id)

    def list_all(self) -> list[WebhookTemplate]:
        return list(self._templates.values())

    def create(self, template_id: str, name: str, event_type: str,
               payload_schema: dict, description: str = "") -> WebhookTemplate:
        t = WebhookTemplate(template_id=template_id, name=name,
                            event_type=event_type, payload_schema=payload_schema,
                            description=description)
        self._templates[template_id] = t
        return t

    def render(self, template_id: str, data: dict) -> dict | None:
        t = self._templates.get(template_id)
        if not t: return None
        return {"event": t.event_type, "data": data, "template": t.template_id}

    def search(self, query: str) -> list[WebhookTemplate]:
        q = query.lower()
        return [t for t in self._templates.values()
                if q in t.name.lower() or q in t.event_type.lower()]
