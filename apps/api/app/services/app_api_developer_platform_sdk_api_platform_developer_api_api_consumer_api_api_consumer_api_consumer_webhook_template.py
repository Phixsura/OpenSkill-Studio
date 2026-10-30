"""Consumer Webhook Template — define reusable payload templates for webhooks."""
from __future__ import annotations
from dataclasses import dataclass, field
import re
import structlog

log = structlog.get_logger()

PLACEHOLDER_RE = re.compile(r"\{\{([a-zA-Z_][a-zA-Z0-9_.]*)\}\}")

@dataclass
class WebhookTemplate:
    template_id: str
    name: str
    content_type: str = "application/json"
    body_template: str = ""
    header_templates: dict[str, str] = field(default_factory=dict)

@dataclass
class RenderResult:
    body: str
    headers: dict[str, str]
    missing_vars: list[str] = field(default_factory=list)

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerWebhookTemplate:
    def __init__(self) -> None:
        self._templates: dict[tuple[str, str], WebhookTemplate] = {}

    def create(self, installation_id: str, template: WebhookTemplate) -> WebhookTemplate:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not template.name:
            raise ValueError("name is required")
        key = (installation_id, template.template_id)
        if key in self._templates:
            raise ValueError(f"Template {template.template_id} already exists")
        self._templates[key] = template
        return template

    def update(self, installation_id: str, template: WebhookTemplate) -> WebhookTemplate:
        key = (installation_id, template.template_id)
        if key not in self._templates:
            raise ValueError("Template not found")
        self._templates[key] = template
        return template

    def render(self, installation_id: str, template_id: str, variables: dict[str, str]) -> RenderResult:
        key = (installation_id, template_id)
        template = self._templates.get(key)
        if not template:
            raise ValueError("Template not found")
        missing: list[str] = []
        # Single-pass substitution to prevent injection
        def replace_var(match: re.Match) -> str:
            var_name = match.group(1)
            if var_name in variables:
                return str(variables[var_name])
            missing.append(var_name)
            return match.group(0)
        body = PLACEHOLDER_RE.sub(replace_var, template.body_template)
        headers = {k: PLACEHOLDER_RE.sub(replace_var, v) for k, v in template.header_templates.items()}
        headers["Content-Type"] = template.content_type
        return RenderResult(body=body, headers=headers, missing_vars=missing)

    def list_variables(self, installation_id: str, template_id: str) -> list[str]:
        template = self._templates.get((installation_id, template_id))
        if not template:
            return []
        all_text = template.body_template + " ".join(template.header_templates.values())
        return sorted(set(PLACEHOLDER_RE.findall(all_text)))

    def list_templates(self, installation_id: str) -> list[WebhookTemplate]:
        return [t for (inst, _), t in self._templates.items() if inst == installation_id]
