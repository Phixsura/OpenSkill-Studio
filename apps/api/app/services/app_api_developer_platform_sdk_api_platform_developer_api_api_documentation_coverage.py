"""API Documentation Coverage — track which endpoints have documentation."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class EndpointDoc:
    endpoint: str
    method: str
    has_description: bool = False
    has_request_schema: bool = False
    has_response_schema: bool = False
    has_examples: bool = False
    has_error_codes: bool = False

    @property
    def coverage_pct(self) -> float:
        checks = [self.has_description, self.has_request_schema, self.has_response_schema, self.has_examples, self.has_error_codes]
        return round(sum(1 for c in checks if c) / len(checks) * 100, 1)

    @property
    def fully_documented(self) -> bool:
        return self.coverage_pct == 100.0

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiDocumentationCoverage:
    def __init__(self) -> None:
        self._docs: dict[tuple[str, str, str], EndpointDoc] = {}

    def register_endpoint(self, installation_id: str, endpoint: str, method: str) -> EndpointDoc:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, method.upper(), endpoint)
        if key not in self._docs:
            self._docs[key] = EndpointDoc(endpoint=endpoint, method=method.upper())
        return self._docs[key]

    def update_coverage(self, installation_id: str, endpoint: str, method: str, **kwargs: bool) -> EndpointDoc:
        key = (installation_id, method.upper(), endpoint)
        doc = self._docs.get(key)
        if doc is None: raise KeyError(f"Endpoint {method} {endpoint} not registered")
        valid = {"has_description", "has_request_schema", "has_response_schema", "has_examples", "has_error_codes"}
        for k, v in kwargs.items():
            if k not in valid: raise ValueError(f"Invalid field: {k}")
            setattr(doc, k, v)
        return doc

    def overall_coverage(self, installation_id: str) -> float:
        docs = [d for (inst, _, _), d in self._docs.items() if inst == installation_id]
        if not docs: return 0.0
        return round(sum(d.coverage_pct for d in docs) / len(docs), 1)

    def undocumented(self, installation_id: str) -> list[EndpointDoc]:
        return [d for (inst, _, _), d in self._docs.items() if inst == installation_id and d.coverage_pct < 100]

    def list_docs(self, installation_id: str) -> list[EndpointDoc]:
        return [d for (inst, _, _), d in self._docs.items() if inst == installation_id]

    def endpoint_count(self, installation_id: str) -> int:
        return sum(1 for (inst, _, _) in self._docs if inst == installation_id)
