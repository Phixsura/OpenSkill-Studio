"""Webhook Templates — pre-built webhook configurations for common providers.

Provides ready-to-use webhook templates for GitHub, Slack, Discord,
Linear, Jira with pre-configured headers, payload transforms, and auth.
"""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class WebhookTemplate:
    template_id: str
    provider: str
    name: str
    description: str
    url_pattern: str
    headers: dict[str, str] = field(default_factory=dict)
    auth_type: str = ""
    events: list[str] = field(default_factory=list)
    icon: str = ""


TEMPLATES = [
    WebhookTemplate("github-push", "github", "GitHub Push", "Trigger on push events",
                    "https://api.github.com/repos/{owner}/{repo}/hooks",
                    {"Accept": "application/vnd.github+json"}, "token",
                    ["push", "pull_request", "issues", "release"], "🐙"),
    WebhookTemplate("slack-notify", "slack", "Slack Notification", "Send to Slack channel",
                    "https://hooks.slack.com/services/{id}",
                    {"Content-Type": "application/json"}, "url",
                    ["message", "alert", "deploy"], "💬"),
    WebhookTemplate("discord-notify", "discord", "Discord Webhook", "Post to Discord",
                    "https://discord.com/api/webhooks/{id}/{token}",
                    {"Content-Type": "application/json"}, "url",
                    ["message", "embed"], "🎮"),
    WebhookTemplate("linear-sync", "linear", "Linear Issue Sync", "Sync with Linear",
                    "https://api.linear.app/graphql",
                    {"Authorization": "Bearer {token}"}, "bearer",
                    ["issue.create", "issue.update"], "📐"),
    WebhookTemplate("jira-sync", "jira", "Jira Issue Sync", "Sync with Jira",
                    "https://{domain}.atlassian.net/rest/webhooks/1.0/webhook",
                    {}, "basic", ["jira:issue_created", "jira:issue_updated"], "🎫"),
]


class WebhookTemplateService:
    """Provides pre-built webhook templates."""

    def __init__(self):
        self._templates = {t.template_id: t for t in TEMPLATES}

    def list_templates(self, provider: str | None = None) -> list[WebhookTemplate]:
        templates = list(self._templates.values())
        if provider:
            templates = [t for t in templates if t.provider == provider]
        return templates

    def get_template(self, template_id: str) -> WebhookTemplate | None:
        return self._templates.get(template_id)

    def get_providers(self) -> list[str]:
        return sorted({t.provider for t in self._templates.values()})

    def search(self, query: str) -> list[WebhookTemplate]:
        q = query.lower()
        return [t for t in self._templates.values()
                if q in t.name.lower() or q in t.provider.lower()
                or q in t.description.lower()]

    def instantiate(self, template_id: str, variables: dict[str, str]) -> dict | None:
        tpl = self._templates.get(template_id)
        if not tpl:
            return None
        url = tpl.url_pattern
        headers = dict(tpl.headers)
        for k, v in variables.items():
            url = url.replace(f"{{{k}}}", v)
            headers = {hk: hv.replace(f"{{{k}}}", v) for hk, hv in headers.items()}
        return {"url": url, "headers": headers, "events": tpl.events, "auth_type": tpl.auth_type}
