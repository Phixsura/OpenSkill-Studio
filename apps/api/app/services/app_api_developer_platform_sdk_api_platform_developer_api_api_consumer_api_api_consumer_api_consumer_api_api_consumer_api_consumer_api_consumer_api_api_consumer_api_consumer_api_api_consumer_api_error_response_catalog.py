"""Consumer API Error Response Catalog — centralized error code registry."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class ErrorDefinition:
    error_code: str
    http_status: int
    title: str
    description: str
    resolution: str = ""
    docs_url: str = ""
    category: str = "general"  # "auth", "validation", "rate_limit", "billing", "internal", "general"

@dataclass
class ErrorLookupResult:
    found: bool
    definition: ErrorDefinition | None = None

VALID_CATEGORIES = {"auth", "validation", "rate_limit", "billing", "internal", "general", "not_found", "permission"}

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiErrorResponseCatalog:
    def __init__(self) -> None:
        self._definitions: dict[tuple[str, str], ErrorDefinition] = {}

    def register(self, installation_id: str, definition: ErrorDefinition) -> ErrorDefinition:
        if not installation_id:
            raise ValueError("installation_id is required")
        if definition.category not in VALID_CATEGORIES:
            raise ValueError(f"Invalid category: {definition.category}")
        if not (400 <= definition.http_status <= 599):
            raise ValueError("http_status must be 4xx or 5xx")
        self._definitions[(installation_id, definition.error_code)] = definition
        return definition

    def lookup(self, installation_id: str, error_code: str) -> ErrorLookupResult:
        defn = self._definitions.get((installation_id, error_code))
        return ErrorLookupResult(found=defn is not None, definition=defn)

    def list_by_category(self, installation_id: str, category: str | None = None) -> list[ErrorDefinition]:
        defs = [d for (inst, _), d in self._definitions.items() if inst == installation_id]
        if category:
            defs = [d for d in defs if d.category == category]
        return sorted(defs, key=lambda d: d.error_code)

    def list_by_status(self, installation_id: str, http_status: int) -> list[ErrorDefinition]:
        return [d for (inst, _), d in self._definitions.items() if inst == installation_id and d.http_status == http_status]

    def search(self, installation_id: str, query: str) -> list[ErrorDefinition]:
        q = query.lower()
        return [d for (inst, _), d in self._definitions.items() if inst == installation_id and (q in d.error_code.lower() or q in d.title.lower() or q in d.description.lower())]
