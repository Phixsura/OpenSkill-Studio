"""App API Developer Webhook Payload Transform Template — reusable payload templates."""
from __future__ import annotations
from dataclasses import dataclass, field
import re
import structlog

log = structlog.get_logger()

@dataclass
class TransformTemplate:
    template_id: str
    name: str
    template: str  # e.g. '{"event": "{{event_type}}", "data": {{payload}}}'
    variables: list[str] = field(default_factory=list)
    usage_count: int = 0

class AppAPIDeveloperAPIApiDeveloperApiApiWebhookPayloadTransformTemplate:
    def __init__(self) -> None:
        self._templates: dict[tuple[str, str], TransformTemplate] = {}

    def create(self, installation_id: str, template_id: str, name: str, template: str) -> TransformTemplate:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, template_id)
        if key in self._templates: raise ValueError(f"Template {template_id} exists")
        variables = re.findall(r"\{\{(\w+)\}\}", template)
        t = TransformTemplate(template_id=template_id, name=name, template=template, variables=variables)
        self._templates[key] = t
        return t

    def apply(self, installation_id: str, template_id: str, values: dict[str, str]) -> str:
        t = self._get(installation_id, template_id)
        # Single-pass substitution prevents re-scanning of substituted values
        import json as _json
        def _escape(val: str) -> str:
            # JSON-safe escape: prevent injection
            return _json.dumps(val)[1:-1]  # strip outer quotes
        result = re.sub(r"\{\{(\w+)\}\}", lambda m: _escape(values.get(m.group(1), "")), t.template)
        t.usage_count += 1
        return result

    def list_templates(self, installation_id: str) -> list[TransformTemplate]:
        return [t for (inst, _), t in self._templates.items() if inst == installation_id]

    def _get(self, installation_id: str, template_id: str) -> TransformTemplate:
        key = (installation_id, template_id)
        t = self._templates.get(key)
        if t is None: raise KeyError(f"Template {template_id} not found")
        return t
