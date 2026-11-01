"""Template Engine — scaffold new extensions from pre-built templates.

Provides templates for common extension types (connector, widget, theme,
automation) and generates project scaffolding with correct structure.
"""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class TemplateFile:
    path: str
    content: str
    is_binary: bool = False


@dataclass
class Template:
    template_id: str
    name: str
    description: str
    category: str
    files: list[TemplateFile] = field(default_factory=list)
    variables: list[str] = field(default_factory=list)


BUILTIN_TEMPLATES: dict[str, Template] = {
    "connector": Template(
        template_id="connector",
        name="Connector Template",
        description="A connector that integrates with an external service",
        category="connector",
        variables=["extension_name", "service_name", "api_base_url"],
        files=[
            TemplateFile("src/connector.py",
                'class {{extension_name}}Connector:\n    BASE_URL = "{{api_base_url}}"\n\n'
                '    def __init__(self, api_key: str):\n        self.api_key = api_key\n\n'
                '    def connect(self) -> dict:\n        return {"status": "connected", "service": "{{service_name}}"}\n'),
            TemplateFile("src/__init__.py", ""),
            TemplateFile("tests/test_connector.py",
                'def test_connect():\n    from src.connector import {{extension_name}}Connector\n'
                '    c = {{extension_name}}Connector("test-key")\n'
                '    assert c.connect()["status"] == "connected"\n'),
            TemplateFile("manifest.json",
                '{"name": "{{extension_name}}", "type": "connector", "version": "0.1.0"}\n'),
        ],
    ),
    "widget": Template(
        template_id="widget",
        name="Dashboard Widget",
        description="A custom widget for the dashboard",
        category="ui",
        variables=["extension_name", "widget_title"],
        files=[
            TemplateFile("src/widget.tsx",
                '"use client";\nexport function {{extension_name}}Widget() {\n'
                '  return <div className="rounded-xl border p-4">\n'
                '    <h3>{{widget_title}}</h3>\n  </div>;\n}\n'),
            TemplateFile("manifest.json",
                '{"name": "{{extension_name}}", "type": "widget", "version": "0.1.0"}\n'),
        ],
    ),
    "automation": Template(
        template_id="automation",
        name="Automation Rule",
        description="An event-driven automation rule",
        category="automation",
        variables=["extension_name", "trigger_event"],
        files=[
            TemplateFile("src/handler.py",
                'def handle_{{trigger_event}}(event: dict) -> dict:\n'
                '    """Handle {{trigger_event}} events."""\n'
                '    return {"processed": True, "event_type": event.get("type")}\n'),
            TemplateFile("manifest.json",
                '{"name": "{{extension_name}}", "type": "automation", '
                '"trigger": "{{trigger_event}}", "version": "0.1.0"}\n'),
        ],
    ),
}


class TemplateEngine:
    """Generates extension scaffolding from templates."""

    def __init__(self):
        self._templates = dict(BUILTIN_TEMPLATES)

    def register_template(self, template: Template) -> None:
        self._templates[template.template_id] = template

    def list_templates(self, category: str | None = None) -> list[Template]:
        templates = list(self._templates.values())
        if category:
            templates = [t for t in templates if t.category == category]
        return templates

    def get_template(self, template_id: str) -> Template | None:
        return self._templates.get(template_id)

    def render(self, template_id: str, variables: dict[str, str]) -> list[TemplateFile] | None:
        """Render a template with variable substitution."""
        template = self._templates.get(template_id)
        if not template:
            return None

        # Check required variables
        missing = [v for v in template.variables if v not in variables]
        if missing:
            return None

        rendered = []
        for f in template.files:
            content = f.content
            path = f.path
            for key, value in variables.items():
                placeholder = "{{" + key + "}}"
                content = content.replace(placeholder, value)
                path = path.replace(placeholder, value)
            rendered.append(TemplateFile(path=path, content=content))
        return rendered
