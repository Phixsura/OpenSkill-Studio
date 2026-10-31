"""API OpenAPI Diff — compare OpenAPI specs across versions to detect changes."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class ApiChange:
    change_type: str  # "endpoint_added", "endpoint_removed", "field_added", "field_removed", "type_changed"
    path: str
    detail: str
    breaking: bool = False

@dataclass
class DiffResult:
    version_from: str
    version_to: str
    changes: list[ApiChange] = field(default_factory=list)
    breaking_count: int = 0
    non_breaking_count: int = 0

BREAKING_CHANGES = {"endpoint_removed", "field_removed", "type_changed"}

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiOpenapiDiff:
    def __init__(self) -> None:
        self._specs: dict[tuple[str, str], dict] = {}  # (installation_id, version) → simplified spec

    def register_spec(self, installation_id: str, version: str, endpoints: dict[str, list[str]], schemas: dict[str, list[str]] | None = None) -> None:
        if not installation_id: raise ValueError("installation_id is required")
        self._specs[(installation_id, version)] = {"endpoints": endpoints, "schemas": schemas or {}}

    def diff(self, installation_id: str, version_from: str, version_to: str) -> DiffResult:
        spec_from = self._specs.get((installation_id, version_from))
        spec_to = self._specs.get((installation_id, version_to))
        if spec_from is None: raise KeyError(f"Spec {version_from} not found")
        if spec_to is None: raise KeyError(f"Spec {version_to} not found")
        changes: list[ApiChange] = []
        ep_from = set(spec_from["endpoints"].keys())
        ep_to = set(spec_to["endpoints"].keys())
        for ep in ep_to - ep_from:
            changes.append(ApiChange("endpoint_added", ep, f"New endpoint: {ep}"))
        for ep in ep_from - ep_to:
            changes.append(ApiChange("endpoint_removed", ep, f"Removed endpoint: {ep}", breaking=True))
        for ep in ep_from & ep_to:
            fields_from = set(spec_from["endpoints"][ep])
            fields_to = set(spec_to["endpoints"][ep])
            for f in fields_to - fields_from:
                changes.append(ApiChange("field_added", f"{ep}.{f}", f"New field: {f}"))
            for f in fields_from - fields_to:
                changes.append(ApiChange("field_removed", f"{ep}.{f}", f"Removed field: {f}", breaking=True))
        breaking = sum(1 for c in changes if c.breaking)
        return DiffResult(version_from=version_from, version_to=version_to, changes=changes, breaking_count=breaking, non_breaking_count=len(changes) - breaking)

    def versions(self, installation_id: str) -> list[str]:
        return sorted({v for (inst, v) in self._specs if inst == installation_id})
