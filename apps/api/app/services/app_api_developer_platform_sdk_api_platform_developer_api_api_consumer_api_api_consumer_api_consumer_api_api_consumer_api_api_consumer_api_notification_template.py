"""Consumer API Notification Template — reusable notification templates."""
from __future__ import annotations
from dataclasses import dataclass, field
import re
from html import escape
import structlog

log = structlog.get_logger()

PLACEHOLDER_RE = re.compile(r"\{\{([a-zA-Z_][a-zA-Z0-9_.]*)\}\}")

@dataclass
class NotificationTemplate:
    template_id: str
    name: str
    channel: str  # "email", "slack", "in_app"
    subject_template: str = ""
    body_template: str = ""
    variables: list[str] = field(default_factory=list)

@dataclass
class RenderedNotification:
    subject: str
    body: str
    channel: str
    missing_vars: list[str] = field(default_factory=list)

VALID_CHANNELS = {"email", "slack", "in_app", "webhook", "sms"}

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiNotificationTemplate:
    def __init__(self) -> None:
        self._templates: dict[tuple[str, str], NotificationTemplate] = {}

    def create(self, installation_id: str, template: NotificationTemplate) -> NotificationTemplate:
        if not installation_id:
            raise ValueError("installation_id is required")
        if template.channel not in VALID_CHANNELS:
            raise ValueError(f"Invalid channel: {template.channel}")
        if not template.name:
            raise ValueError("name is required")
        # Extract variables
        all_text = template.subject_template + " " + template.body_template
        template.variables = sorted(set(PLACEHOLDER_RE.findall(all_text)))
        key = (installation_id, template.template_id)
        if key in self._templates:
            raise ValueError(f"Template {template.template_id} already exists")
        self._templates[key] = template
        return template

    def render(self, installation_id: str, template_id: str, variables: dict[str, str]) -> RenderedNotification:
        key = (installation_id, template_id)
        template = self._templates.get(key)
        if not template:
            raise ValueError("Template not found")
        missing: list[str] = []
        def replace(match: re.Match) -> str:
            var = match.group(1)
            if var in variables:
                return escape(str(variables[var]))
            missing.append(var)
            return match.group(0)
        subject = PLACEHOLDER_RE.sub(replace, template.subject_template)
        body = PLACEHOLDER_RE.sub(replace, template.body_template)
        return RenderedNotification(subject=subject, body=body, channel=template.channel, missing_vars=missing)

    def get(self, installation_id: str, template_id: str) -> NotificationTemplate | None:
        return self._templates.get((installation_id, template_id))

    def list_templates(self, installation_id: str, channel: str | None = None) -> list[NotificationTemplate]:
        templates = [t for (inst, _), t in self._templates.items() if inst == installation_id]
        if channel:
            templates = [t for t in templates if t.channel == channel]
        return sorted(templates, key=lambda t: t.name)
