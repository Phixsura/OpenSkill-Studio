"""Consumer Webhook Template — reusable webhook payload templates."""
from __future__ import annotations

import re
import structlog
from dataclasses import dataclass, field

logger = structlog.get_logger()

PLACEHOLDER_RE = re.compile(r"\{\{(\w+(?:\.\w+)*)\}\}")


@dataclass
class WebhookTemplate:
    template_id: str
    name: str
    event_type: str
    body_template: dict
    headers_template: dict[str, str] = field(default_factory=dict)
    description: str = ""


@dataclass
class TemplateManager:
    """Manage reusable webhook payload templates with variable substitution."""

    _templates: dict[str, WebhookTemplate] = field(default_factory=dict)

    def create(self, template: WebhookTemplate) -> dict:
        if template.template_id in self._templates:
            raise ValueError(f"Template {template.template_id} already exists")
        if not template.body_template:
            raise ValueError("Body template is required")
        self._templates[template.template_id] = template
        logger.info("template_created", template_id=template.template_id)
        placeholders = self._extract_placeholders(template.body_template)
        return {"template_id": template.template_id, "placeholders": placeholders}

    def _extract_placeholders(self, obj: dict | list | str) -> list[str]:
        placeholders: set[str] = set()
        if isinstance(obj, str):
            placeholders.update(PLACEHOLDER_RE.findall(obj))
        elif isinstance(obj, dict):
            for v in obj.values():
                placeholders.update(self._extract_placeholders(v))
        elif isinstance(obj, list):
            for item in obj:
                placeholders.update(self._extract_placeholders(item))
        return sorted(placeholders)

    def _substitute(self, obj, variables: dict):
        if isinstance(obj, str):
            def replacer(m):
                key = m.group(1)
                parts = key.split(".")
                val = variables
                for p in parts:
                    if isinstance(val, dict):
                        val = val.get(p, m.group(0))
                    else:
                        return m.group(0)
                return str(val)
            return PLACEHOLDER_RE.sub(replacer, obj)
        elif isinstance(obj, dict):
            return {k: self._substitute(v, variables) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._substitute(item, variables) for item in obj]
        return obj

    def render(self, template_id: str, variables: dict) -> dict:
        template = self._templates.get(template_id)
        if not template:
            raise ValueError(f"Template {template_id} not found")
        body = self._substitute(template.body_template, variables)
        headers = {k: self._substitute(v, variables)
                    for k, v in template.headers_template.items()}
        return {"body": body, "headers": headers, "event_type": template.event_type}

    def preview(self, template_id: str) -> dict:
        template = self._templates.get(template_id)
        if not template:
            raise ValueError(f"Template {template_id} not found")
        placeholders = self._extract_placeholders(template.body_template)
        return {
            "template_id": template.template_id,
            "name": template.name,
            "event_type": template.event_type,
            "body_template": template.body_template,
            "placeholders": placeholders,
        }

    def list_templates(self, event_type: str | None = None) -> list[dict]:
        templates = list(self._templates.values())
        if event_type:
            templates = [t for t in templates if t.event_type == event_type]
        return [
            {"template_id": t.template_id, "name": t.name,
             "event_type": t.event_type, "description": t.description}
            for t in templates
        ]

    def delete(self, template_id: str) -> dict:
        if template_id in self._templates:
            del self._templates[template_id]
            return {"deleted": True}
        return {"deleted": False}

    def clone(self, source_id: str, new_id: str, new_name: str) -> dict:
        source = self._templates.get(source_id)
        if not source:
            raise ValueError(f"Template {source_id} not found")
        if new_id in self._templates:
            raise ValueError(f"Template {new_id} already exists")
        cloned = WebhookTemplate(
            template_id=new_id, name=new_name,
            event_type=source.event_type,
            body_template=dict(source.body_template),
            headers_template=dict(source.headers_template),
        )
        self._templates[new_id] = cloned
        return {"template_id": new_id, "cloned_from": source_id}
