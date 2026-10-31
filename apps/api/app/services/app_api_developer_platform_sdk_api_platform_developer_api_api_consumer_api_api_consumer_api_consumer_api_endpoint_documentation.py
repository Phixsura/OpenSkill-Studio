"""Consumer API Endpoint Documentation — auto-generate per-endpoint API docs."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class ParamDoc:
    name: str
    location: str  # "path", "query", "header", "body"
    param_type: str  # "string", "integer", "boolean", "array", "object"
    required: bool = True
    description: str = ""
    example: str = ""

@dataclass
class EndpointDoc:
    endpoint_id: str
    method: str
    path: str
    summary: str
    description: str = ""
    params: list[ParamDoc] = field(default_factory=list)
    response_example: str = ""
    tags: list[str] = field(default_factory=list)
    deprecated: bool = False

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiEndpointDocumentation:
    def __init__(self) -> None:
        self._docs: dict[tuple[str, str], EndpointDoc] = {}

    def register(self, installation_id: str, doc: EndpointDoc) -> EndpointDoc:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not doc.summary:
            raise ValueError("summary is required")
        self._docs[(installation_id, doc.endpoint_id)] = doc
        return doc

    def get(self, installation_id: str, endpoint_id: str) -> EndpointDoc | None:
        return self._docs.get((installation_id, endpoint_id))

    def list_by_tag(self, installation_id: str, tag: str) -> list[EndpointDoc]:
        return [d for (inst, _), d in self._docs.items() if inst == installation_id and tag in d.tags]

    def search(self, installation_id: str, query: str) -> list[EndpointDoc]:
        q = query.lower()
        return [d for (inst, _), d in self._docs.items() if inst == installation_id and (q in d.summary.lower() or q in d.description.lower() or q in d.path.lower())]

    def list_all(self, installation_id: str, include_deprecated: bool = True) -> list[EndpointDoc]:
        docs = [d for (inst, _), d in self._docs.items() if inst == installation_id]
        if not include_deprecated:
            docs = [d for d in docs if not d.deprecated]
        return sorted(docs, key=lambda d: (d.tags[0] if d.tags else "", d.path))

    def get_tags(self, installation_id: str) -> list[str]:
        tags: set[str] = set()
        for (inst, _), d in self._docs.items():
            if inst == installation_id:
                tags.update(d.tags)
        return sorted(tags)
