"""API Consumer Playground Template — pre-built request templates for API playground."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class PlaygroundTemplate:
    template_id: str
    name: str
    method: str
    path: str
    headers: dict[str, str] = field(default_factory=dict)
    body_template: str = ""
    description: str = ""
    category: str = "general"
    variables: list[str] = field(default_factory=list)  # placeholders like {{user_id}}
    usage_count: int = 0

VALID_CATEGORIES = {"general", "authentication", "crud", "webhooks", "search", "admin"}

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiPlaygroundTemplate:
    def __init__(self) -> None:
        self._templates: dict[tuple[str, str], PlaygroundTemplate] = {}

    def create_template(self, installation_id: str, template: PlaygroundTemplate) -> PlaygroundTemplate:
        if not installation_id: raise ValueError("installation_id is required")
        if not template.name: raise ValueError("name is required")
        if template.category not in VALID_CATEGORIES: raise ValueError(f"Invalid category: {template.category}")
        key = (installation_id, template.template_id)
        if key in self._templates: raise ValueError(f"Template {template.template_id} exists")
        self._templates[key] = template
        return template

    def use_template(self, installation_id: str, template_id: str, variables: dict[str, str] | None = None) -> dict[str, str]:
        t = self._get(installation_id, template_id)
        t.usage_count += 1
        body = t.body_template
        for var_name, var_val in (variables or {}).items():
            body = body.replace(f"{{{{{var_name}}}}}", var_val)
        return {"method": t.method, "path": t.path, "body": body, "headers": dict(t.headers)}

    def by_category(self, installation_id: str) -> dict[str, list[PlaygroundTemplate]]:
        result: dict[str, list[PlaygroundTemplate]] = {}
        for (inst, _), t in self._templates.items():
            if inst == installation_id:
                result.setdefault(t.category, []).append(t)
        return result

    def most_used(self, installation_id: str, limit: int = 5) -> list[PlaygroundTemplate]:
        templates = [t for (inst, _), t in self._templates.items() if inst == installation_id]
        return sorted(templates, key=lambda t: -t.usage_count)[:limit]

    def list_templates(self, installation_id: str) -> list[PlaygroundTemplate]:
        return [t for (inst, _), t in self._templates.items() if inst == installation_id]

    def _get(self, installation_id: str, template_id: str) -> PlaygroundTemplate:
        t = self._templates.get((installation_id, template_id))
        if t is None: raise KeyError(f"Template {template_id} not found")
        return t
