"""App API Developer API Documentation Generator — auto-generate API docs from schemas."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class EndpointDoc:
    method: str
    path: str
    summary: str
    parameters: list[dict] = field(default_factory=list)
    request_body: dict | None = None
    response_schema: dict | None = None
    examples: list[dict] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)

@dataclass
class APIDocumentation:
    title: str
    version: str
    endpoints: list[EndpointDoc] = field(default_factory=list)

    @property
    def endpoint_count(self) -> int:
        return len(self.endpoints)

    @property
    def documented_pct(self) -> float:
        if not self.endpoints: return 0.0
        with_examples = sum(1 for e in self.endpoints if e.examples)
        return round(with_examples / len(self.endpoints) * 100, 1)

class AppAPIDeveloperAPIApiDeveloperApiApiApiDocumentationGenerator:
    def __init__(self) -> None:
        self._docs: dict[str, APIDocumentation] = {}

    def create(self, installation_id: str, title: str, version: str) -> APIDocumentation:
        if not installation_id: raise ValueError("installation_id is required")
        doc = APIDocumentation(title=title, version=version)
        self._docs[installation_id] = doc
        return doc

    def add_endpoint(self, installation_id: str, method: str, path: str, summary: str, parameters: list[dict] | None = None, request_body: dict | None = None, response_schema: dict | None = None, examples: list[dict] | None = None, tags: list[str] | None = None) -> EndpointDoc:
        doc = self._docs.get(installation_id)
        if doc is None: raise KeyError("No documentation created")
        ep = EndpointDoc(method=method.upper(), path=path, summary=summary, parameters=parameters or [], request_body=request_body, response_schema=response_schema, examples=examples or [], tags=tags or [])
        doc.endpoints.append(ep)
        return ep

    def get(self, installation_id: str) -> APIDocumentation | None:
        return self._docs.get(installation_id)

    def render_markdown(self, installation_id: str) -> str:
        doc = self._docs.get(installation_id)
        if doc is None: raise KeyError("No documentation")
        lines = [f"# {doc.title} (v{doc.version})", ""]
        for ep in doc.endpoints:
            lines.append(f"## {ep.method} {ep.path}")
            lines.append(f"\n{ep.summary}\n")
            if ep.parameters:
                lines.append("### Parameters")
                for p in ep.parameters:
                    lines.append(f"- `{p.get('name', '')}` ({p.get('type', 'string')}): {p.get('description', '')}")
        return "\n".join(lines)
