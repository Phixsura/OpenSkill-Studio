"""API Consumer Endpoint Documentation — manage per-endpoint API documentation."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class EndpointDoc:
    endpoint: str
    method: str
    summary: str
    description: str = ""
    parameters: list[dict[str, str]] = field(default_factory=list)
    request_example: str = ""
    response_example: str = ""
    tags: list[str] = field(default_factory=list)

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiEndpointDocumentation:
    def __init__(self) -> None:
        self._docs: dict[tuple[str, str, str], EndpointDoc] = {}

    def set_doc(self, installation_id: str, doc: EndpointDoc) -> EndpointDoc:
        if not installation_id: raise ValueError("installation_id is required")
        if not doc.summary: raise ValueError("summary is required")
        self._docs[(installation_id, doc.method.upper(), doc.endpoint)] = doc
        return doc

    def get_doc(self, installation_id: str, method: str, endpoint: str) -> EndpointDoc | None:
        return self._docs.get((installation_id, method.upper(), endpoint))

    def search(self, installation_id: str, query: str) -> list[EndpointDoc]:
        q = query.lower()
        return [d for (inst, _, _), d in self._docs.items()
                if inst == installation_id and (q in d.summary.lower() or q in d.description.lower() or q in d.endpoint.lower())]

    def by_tag(self, installation_id: str, tag: str) -> list[EndpointDoc]:
        return [d for (inst, _, _), d in self._docs.items() if inst == installation_id and tag in d.tags]

    def undocumented_count(self, installation_id: str, all_endpoints: list[tuple[str, str]]) -> int:
        return sum(1 for m, ep in all_endpoints if (installation_id, m.upper(), ep) not in self._docs)

    def list_docs(self, installation_id: str) -> list[EndpointDoc]:
        return [d for (inst, _, _), d in self._docs.items() if inst == installation_id]
