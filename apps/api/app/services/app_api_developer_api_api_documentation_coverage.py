"""App API Developer API Documentation Coverage — track undocumented endpoints."""
from __future__ import annotations
from dataclasses import dataclass
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

    @property
    def coverage_score(self) -> int:
        return sum([self.has_description, self.has_request_schema, self.has_response_schema, self.has_examples])

    @property
    def fully_documented(self) -> bool:
        return self.coverage_score == 4

class AppAPIDeveloperAPIApiDocumentationCoverage:
    def __init__(self) -> None:
        self._docs: dict[tuple[str, str, str], EndpointDoc] = {}

    def register(self, installation_id: str, endpoint: str, method: str, has_description: bool = False, has_request_schema: bool = False, has_response_schema: bool = False, has_examples: bool = False) -> EndpointDoc:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, method.upper(), endpoint)
        d = EndpointDoc(endpoint=endpoint, method=method.upper(), has_description=has_description, has_request_schema=has_request_schema, has_response_schema=has_response_schema, has_examples=has_examples)
        self._docs[key] = d
        return d

    def coverage_pct(self, installation_id: str) -> float:
        docs = [d for (inst, _, _), d in self._docs.items() if inst == installation_id]
        if not docs: return 0.0
        total_score = sum(d.coverage_score for d in docs)
        return round(total_score / (len(docs) * 4) * 100, 1)

    def undocumented(self, installation_id: str) -> list[EndpointDoc]:
        return [d for (inst, _, _), d in self._docs.items() if inst == installation_id and not d.fully_documented]

    def fully_documented_count(self, installation_id: str) -> int:
        return sum(1 for (inst, _, _), d in self._docs.items() if inst == installation_id and d.fully_documented)

    def all_endpoints(self, installation_id: str) -> list[EndpointDoc]:
        return [d for (inst, _, _), d in self._docs.items() if inst == installation_id]
