"""App API Developer Endpoint Response Schema Tracker — detect response schema drift."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class ResponseSchema:
    endpoint: str
    method: str
    expected_fields: set[str]
    observed_fields: set[str] = field(default_factory=set)
    check_count: int = 0
    drift_count: int = 0

    @property
    def has_drift(self) -> bool:
        return self.observed_fields != self.expected_fields and self.check_count > 0

    @property
    def missing_fields(self) -> set[str]:
        return self.expected_fields - self.observed_fields

    @property
    def extra_fields(self) -> set[str]:
        return self.observed_fields - self.expected_fields

class AppAPIDeveloperAPIApiDeveloperApiApiEndpointResponseSchemaTracker:
    def __init__(self) -> None:
        self._schemas: dict[tuple[str, str, str], ResponseSchema] = {}

    def register(self, installation_id: str, endpoint: str, method: str, expected_fields: list[str]) -> ResponseSchema:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, method.upper(), endpoint)
        s = ResponseSchema(endpoint=endpoint, method=method.upper(), expected_fields=set(expected_fields))
        self._schemas[key] = s
        return s

    def check(self, installation_id: str, endpoint: str, method: str, response_fields: list[str]) -> ResponseSchema:
        key = (installation_id, method.upper(), endpoint)
        s = self._schemas.get(key)
        if s is None: raise KeyError(f"No schema for {method} {endpoint}")
        s.observed_fields = set(response_fields)
        s.check_count += 1
        if s.has_drift: s.drift_count += 1
        return s

    def drifted(self, installation_id: str) -> list[ResponseSchema]:
        return [s for (inst, _, _), s in self._schemas.items() if inst == installation_id and s.has_drift]

    def all_schemas(self, installation_id: str) -> list[ResponseSchema]:
        return [s for (inst, _, _), s in self._schemas.items() if inst == installation_id]
