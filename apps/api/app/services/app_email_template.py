"""App Email Template — manage and render email templates.

Manages email templates for installed apps:
- Register templates with subject and body
- Variable substitution in subject and body
- HTML and plain text support
- Per-installation scoped templates
"""

from __future__ import annotations

import html
import re
from dataclasses import dataclass

import structlog

log = structlog.get_logger()

_VAR_RE = re.compile(r"\{\{(\w+)\}\}")


@dataclass
class EmailTemplate:
    """An email template."""

    template_id: str
    name: str
    subject: str
    body_html: str
    body_text: str = ""


@dataclass
class RenderedEmail:
    """A rendered email ready for sending."""

    subject: str
    body_html: str
    body_text: str
    to: str
    variables_used: list[str]


class AppEmailTemplate:
    """Manage and render email templates."""

    def __init__(self) -> None:
        self._templates: dict[tuple[str, str], EmailTemplate] = {}

    def register(
        self,
        installation_id: str,
        template_id: str,
        name: str,
        subject: str,
        body_html: str,
        body_text: str = "",
    ) -> EmailTemplate:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not template_id:
            raise ValueError("template_id is required")
        if not subject:
            raise ValueError("subject is required")
        if not body_html:
            raise ValueError("body_html is required")

        tpl = EmailTemplate(
            template_id=template_id, name=name,
            subject=subject, body_html=body_html, body_text=body_text,
        )
        self._templates[(installation_id, template_id)] = tpl
        return tpl

    def render(
        self,
        installation_id: str,
        template_id: str,
        to: str,
        variables: dict[str, str],
    ) -> RenderedEmail:
        """Render a template with variables."""
        if not to:
            raise ValueError("to is required")

        tpl = self._get(installation_id, template_id)
        used: list[str] = []

        def replace_var(text: str, escape: bool = False) -> str:
            def sub(m: re.Match) -> str:
                key = m.group(1)
                if key not in used:
                    used.append(key)
                val = variables.get(key, "")
                return html.escape(val) if escape else val
            return _VAR_RE.sub(sub, text)

        return RenderedEmail(
            subject=replace_var(tpl.subject),
            body_html=replace_var(tpl.body_html, escape=True),
            body_text=replace_var(tpl.body_text or tpl.body_html, escape=False),
            to=to,
            variables_used=sorted(set(used)),
        )

    def list_templates(self, installation_id: str) -> list[EmailTemplate]:
        return [t for (inst, _), t in self._templates.items() if inst == installation_id]

    def _get(self, installation_id: str, template_id: str) -> EmailTemplate:
        key = (installation_id, template_id)
        tpl = self._templates.get(key)
        if tpl is None:
            raise KeyError(f"Template {template_id} not found")
        return tpl
