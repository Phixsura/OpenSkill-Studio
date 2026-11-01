"""Starter Template — curated starter templates for extension development.

Provides pre-configured templates for common extension patterns with
customizable variables, preview, and one-click initialization.
"""
from __future__ import annotations
import secrets
from dataclasses import dataclass, field
from enum import Enum


class TemplateCategory(str, Enum):
    INTEGRATION = "integration"
    AUTOMATION = "automation"
    ANALYTICS = "analytics"
    UI_WIDGET = "ui_widget"
    DATA_SYNC = "data_sync"
    WEBHOOK = "webhook"


@dataclass
class TemplateVariable:
    name: str
    label: str
    default: str = ""
    required: bool = True
    placeholder: str = ""


@dataclass
class StarterTemplate:
    template_id: str
    name: str
    description: str
    category: TemplateCategory
    runtime: str
    variables: list[TemplateVariable] = field(default_factory=list)
    files: dict[str, str] = field(default_factory=dict)  # path -> content template
    popularity: int = 0
    tags: list[str] = field(default_factory=list)


class StarterTemplateService:
    """Manages curated starter templates for extension developers."""

    def __init__(self):
        self._templates: dict[str, StarterTemplate] = {}

    def register_template(self, name: str, description: str,
                          category: TemplateCategory, runtime: str,
                          variables: list[dict] | None = None,
                          files: dict[str, str] | None = None,
                          tags: list[str] | None = None) -> StarterTemplate:
        template_id = f"tpl_{secrets.token_urlsafe(8)}"
        parsed_vars = [
            TemplateVariable(
                name=v["name"], label=v.get("label", v["name"]),
                default=v.get("default", ""), required=v.get("required", True),
                placeholder=v.get("placeholder", ""),
            )
            for v in (variables or [])
        ]
        template = StarterTemplate(
            template_id=template_id, name=name, description=description,
            category=category, runtime=runtime,
            variables=parsed_vars, files=files or {},
            tags=tags or [],
        )
        self._templates[template_id] = template
        return template

    def instantiate(self, template_id: str,
                    values: dict[str, str]) -> dict[str, str] | dict:
        template = self._templates.get(template_id)
        if not template:
            return {"error": "Template not found"}

        # Validate required variables
        for var in template.variables:
            if var.required and var.name not in values:
                if var.default:
                    values[var.name] = var.default
                else:
                    return {"error": f"Missing required variable: {var.name}"}

        # Apply variable substitution
        result: dict[str, str] = {}
        for path, content in template.files.items():
            resolved_path = self._substitute(path, values)
            resolved_content = self._substitute(content, values)
            result[resolved_path] = resolved_content

        template.popularity += 1
        return result

    def _substitute(self, text: str, values: dict[str, str]) -> str:
        result = text
        for key, val in values.items():
            result = result.replace(f"{{{{{key}}}}}", val)
        return result

    def search(self, query: str = "", category: TemplateCategory | None = None,
               runtime: str | None = None) -> list[StarterTemplate]:
        templates = list(self._templates.values())
        if category:
            templates = [t for t in templates if t.category == category]
        if runtime:
            templates = [t for t in templates if t.runtime == runtime]
        if query:
            q = query.lower()
            templates = [t for t in templates
                         if q in t.name.lower() or q in t.description.lower()
                         or any(q in tag for tag in t.tags)]
        return sorted(templates, key=lambda t: t.popularity, reverse=True)

    def get_popular(self, limit: int = 10) -> list[StarterTemplate]:
        return sorted(self._templates.values(),
                      key=lambda t: t.popularity, reverse=True)[:limit]
