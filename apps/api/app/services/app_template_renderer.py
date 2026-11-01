"""App Template Renderer — render templates with variable substitution.

Renders templates for installed apps:
- Mustache-style variable substitution ({{variable}})
- Conditional blocks ({{#if}}/{{/if}})
- Loop blocks ({{#each}}/{{/each}})
- HTML escaping by default
- Template registration and caching
"""

from __future__ import annotations

import html
import re
from dataclasses import dataclass

import structlog

log = structlog.get_logger()

_VAR_RE = re.compile(r"\{\{(\w+(?:\.\w+)*)\}\}")
_IF_RE = re.compile(r"\{\{#if\s+(\w+)\}\}(.*?)\{\{/if\}\}", re.DOTALL)
_EACH_RE = re.compile(r"\{\{#each\s+(\w+)\}\}(.*?)\{\{/each\}\}", re.DOTALL)


@dataclass
class Template:
    """A registered template."""

    template_id: str
    content: str
    content_type: str = "text/html"


@dataclass
class RenderResult:
    """Result of rendering a template."""

    output: str
    template_id: str
    variables_used: list[str]


def _resolve(key: str, ctx: dict) -> object:
    """Resolve a dotted key from context."""
    parts = key.split(".")
    val: object = ctx
    for part in parts:
        if isinstance(val, dict):
            val = val.get(part)
        else:
            return None
    return val


class AppTemplateRenderer:
    """Render templates with variable substitution."""

    def __init__(self) -> None:
        # (installation_id, template_id) → Template
        self._templates: dict[tuple[str, str], Template] = {}

    def register_template(
        self,
        installation_id: str,
        template_id: str,
        content: str,
        content_type: str = "text/html",
    ) -> Template:
        """Register a template."""
        if not installation_id:
            raise ValueError("installation_id is required")
        if not template_id:
            raise ValueError("template_id is required")
        if not content:
            raise ValueError("content is required")

        tpl = Template(
            template_id=template_id,
            content=content,
            content_type=content_type,
        )
        self._templates[(installation_id, template_id)] = tpl
        return tpl

    def render(
        self,
        installation_id: str,
        template_id: str,
        variables: dict,
        escape_html: bool = True,
    ) -> RenderResult:
        """Render a template with variables."""
        tpl = self._get(installation_id, template_id)
        output = tpl.content
        used: list[str] = []

        # Process {{#each}} blocks
        def each_replace(m: re.Match) -> str:
            key = m.group(1)
            body = m.group(2)
            items = _resolve(key, variables)
            if not isinstance(items, list):
                return ""
            used.append(key)
            parts = []
            for item in items:
                rendered = body
                if isinstance(item, dict):
                    for k, v in item.items():
                        val = html.escape(str(v)) if escape_html else str(v)
                        rendered = rendered.replace(f"{{{{{k}}}}}", val)
                else:
                    val = html.escape(str(item)) if escape_html else str(item)
                    rendered = rendered.replace("{{.}}", val)
                parts.append(rendered)
            return "".join(parts)

        output = _EACH_RE.sub(each_replace, output)

        # Process {{#if}} blocks
        def if_replace(m: re.Match) -> str:
            key = m.group(1)
            body = m.group(2)
            val = _resolve(key, variables)
            used.append(key)
            if val:
                return body
            return ""

        output = _IF_RE.sub(if_replace, output)

        # Process {{variable}} substitutions
        def var_replace(m: re.Match) -> str:
            key = m.group(1)
            val = _resolve(key, variables)
            used.append(key)
            if val is None:
                return ""
            s = str(val)
            return html.escape(s) if escape_html else s

        output = _VAR_RE.sub(var_replace, output)

        return RenderResult(
            output=output,
            template_id=template_id,
            variables_used=sorted(set(used)),
        )

    def get_template(self, installation_id: str, template_id: str) -> Template:
        return self._get(installation_id, template_id)

    def list_templates(self, installation_id: str) -> list[Template]:
        return [
            tpl for (inst, _), tpl in self._templates.items()
            if inst == installation_id
        ]

    def _get(self, installation_id: str, template_id: str) -> Template:
        key = (installation_id, template_id)
        tpl = self._templates.get(key)
        if tpl is None:
            raise KeyError(f"Template {template_id} not found")
        return tpl
