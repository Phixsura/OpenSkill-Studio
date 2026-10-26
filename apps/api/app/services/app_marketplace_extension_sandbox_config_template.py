"""Sandbox Config Template — templated configuration with variable substitution.

Defines config templates with typed variables, defaults, validation,
and renders final configs from templates + variable values.
"""
from __future__ import annotations
import re
from dataclasses import dataclass, field


@dataclass
class TemplateVariable:
    name: str
    var_type: str  # string, integer, boolean, enum
    default: str = ""
    required: bool = True
    enum_values: list[str] | None = None
    description: str = ""


@dataclass
class ConfigTemplate:
    template_id: str
    name: str
    content: dict[str, str]  # key -> template string with {{vars}}
    variables: list[TemplateVariable] = field(default_factory=list)


VAR_RE = re.compile(r"\{\{(\w+)\}\}")


class SandboxConfigTemplateService:
    """Renders configs from templates with variable substitution."""

    def __init__(self):
        self._templates: dict[str, ConfigTemplate] = {}

    def register(self, template_id: str, name: str, content: dict[str, str],
                 variables: list[dict]) -> ConfigTemplate:
        parsed_vars = [TemplateVariable(
            name=v["name"], var_type=v.get("type", "string"),
            default=str(v.get("default", "")), required=v.get("required", True),
            enum_values=v.get("enum"), description=v.get("description", ""),
        ) for v in variables]
        tpl = ConfigTemplate(template_id=template_id, name=name,
                             content=content, variables=parsed_vars)
        self._templates[template_id] = tpl
        return tpl

    def render(self, template_id: str, values: dict[str, str]) -> dict | list:
        tpl = self._templates.get(template_id)
        if not tpl:
            return {"error": "Template not found"}

        # Validate and apply defaults
        errors = []
        resolved: dict[str, str] = {}
        for var in tpl.variables:
            val = values.get(var.name, var.default)
            if not val and var.required:
                errors.append(f"Missing required: {var.name}")
                continue
            if var.enum_values and val and val not in var.enum_values:
                errors.append(f"{var.name}: must be one of {var.enum_values}")
                continue
            resolved[var.name] = val

        if errors:
            return {"error": "Validation failed", "errors": errors}

        # Substitute
        result: dict[str, str] = {}
        for key, template_str in tpl.content.items():
            rendered = template_str
            for var_name, var_val in resolved.items():
                rendered = rendered.replace(f"{{{{{var_name}}}}}", var_val)
            # Check for unresolved vars
            remaining = VAR_RE.findall(rendered)
            if remaining:
                errors.append(f"Unresolved variables in {key}: {remaining}")
            result[key] = rendered

        if errors:
            return {"error": "Render failed", "errors": errors}
        return result

    def get_variables(self, template_id: str) -> list[TemplateVariable]:
        tpl = self._templates.get(template_id)
        return tpl.variables if tpl else []

    def list_templates(self) -> list[dict]:
        return [{"id": t.template_id, "name": t.name, "vars": len(t.variables)}
                for t in self._templates.values()]
