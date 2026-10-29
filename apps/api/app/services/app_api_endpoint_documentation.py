"""App API Endpoint Documentation — per-endpoint documentation."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class EndpointDoc:
    method: str
    path: str
    summary: str
    description: str = ""
    parameters: list[str] = field(default_factory=list)
    response_example: str = ""

class AppAPIEndpointDocumentation:
    def __init__(self) -> None:
        self._docs: dict[tuple[str, str, str], EndpointDoc] = {}

    def document(self, installation_id: str, method: str, path: str, summary: str, description: str = "", parameters: list[str] | None = None, response_example: str = "") -> EndpointDoc:
        if not installation_id: raise ValueError("installation_id is required")
        doc = EndpointDoc(method=method.upper(), path=path, summary=summary, description=description, parameters=parameters or [], response_example=response_example)
        self._docs[(installation_id, method.upper(), path)] = doc
        return doc

    def get_doc(self, installation_id: str, method: str, path: str) -> EndpointDoc | None:
        return self._docs.get((installation_id, method.upper(), path))

    def undocumented(self, installation_id: str, all_endpoints: list[tuple[str, str]]) -> list[tuple[str, str]]:
        documented = {(m, p) for (inst, m, p) in self._docs if inst == installation_id}
        return [(m, p) for m, p in all_endpoints if (m, p) not in documented]

    def list_docs(self, installation_id: str) -> list[EndpointDoc]:
        return [d for (inst, _, _), d in self._docs.items() if inst == installation_id]
