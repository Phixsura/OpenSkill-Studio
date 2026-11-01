"""Documentation Generator — auto-generate API docs for extensions.

Parses extension manifests and code metadata to produce structured
API documentation including endpoints, schemas, and examples.
"""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class APIEndpoint:
    method: str
    path: str
    description: str
    params: list[dict] = field(default_factory=list)
    request_body: dict | None = None
    response_schema: dict | None = None
    example_response: dict | None = None


@dataclass
class DocSection:
    title: str
    content: str
    subsections: list["DocSection"] = field(default_factory=list)


class DocGenerator:
    """Generates structured documentation from extension metadata."""

    def __init__(self):
        self._endpoints: dict[str, list[APIEndpoint]] = {}
        self._sections: dict[str, list[DocSection]] = {}

    def register_endpoint(self, extension_id: str, endpoint: APIEndpoint) -> None:
        self._endpoints.setdefault(extension_id, []).append(endpoint)

    def add_section(self, extension_id: str, section: DocSection) -> None:
        self._sections.setdefault(extension_id, []).append(section)

    def generate_markdown(self, extension_id: str, title: str = "") -> str:
        """Generate markdown documentation for an extension."""
        lines = [f"# {title or extension_id}", ""]

        # Custom sections
        for section in self._sections.get(extension_id, []):
            lines.extend(self._render_section(section, level=2))

        # API Reference
        endpoints = self._endpoints.get(extension_id, [])
        if endpoints:
            lines.append("## API Reference")
            lines.append("")
            for ep in endpoints:
                lines.append(f"### `{ep.method} {ep.path}`")
                lines.append("")
                lines.append(ep.description)
                lines.append("")
                if ep.params:
                    lines.append("**Parameters:**")
                    lines.append("")
                    for p in ep.params:
                        req = " *(required)*" if p.get("required") else ""
                        lines.append(f"- `{p['name']}` ({p.get('type', 'string')}){req}: {p.get('description', '')}")
                    lines.append("")
                if ep.request_body:
                    lines.append("**Request Body:**")
                    lines.append(f"```json\n{ep.request_body}\n```")
                    lines.append("")
                if ep.example_response:
                    lines.append("**Example Response:**")
                    lines.append(f"```json\n{ep.example_response}\n```")
                    lines.append("")

        return "\n".join(lines)

    def _render_section(self, section: DocSection, level: int) -> list[str]:
        lines = [f"{'#' * level} {section.title}", "", section.content, ""]
        for sub in section.subsections:
            lines.extend(self._render_section(sub, level + 1))
        return lines

    def generate_openapi_stub(self, extension_id: str) -> dict:
        """Generate an OpenAPI 3.0 stub from registered endpoints."""
        paths: dict[str, dict] = {}
        for ep in self._endpoints.get(extension_id, []):
            method = ep.method.lower()
            path_item = paths.setdefault(ep.path, {})
            operation: dict = {"summary": ep.description}
            if ep.params:
                operation["parameters"] = [
                    {"name": p["name"], "in": "query", "required": p.get("required", False),
                     "schema": {"type": p.get("type", "string")}}
                    for p in ep.params
                ]
            if ep.response_schema:
                operation["responses"] = {"200": {"description": "OK", "content": {
                    "application/json": {"schema": ep.response_schema}}}}
            else:
                operation["responses"] = {"200": {"description": "OK"}}
            path_item[method] = operation
        return {
            "openapi": "3.0.0",
            "info": {"title": extension_id, "version": "1.0.0"},
            "paths": paths,
        }
