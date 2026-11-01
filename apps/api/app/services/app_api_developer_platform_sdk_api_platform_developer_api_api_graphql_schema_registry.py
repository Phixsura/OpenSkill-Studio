"""API GraphQL Schema Registry — manage and version GraphQL schemas."""
from __future__ import annotations
from dataclasses import dataclass, field
import hashlib
import time
import structlog

log = structlog.get_logger()

@dataclass
class SchemaVersion:
    version: str
    schema_hash: str
    type_count: int = 0
    query_count: int = 0
    mutation_count: int = 0
    published_at: float = field(default_factory=time.time)
    breaking_changes: list[str] = field(default_factory=list)

@dataclass
class SchemaRegistry:
    registry_id: str
    service_name: str
    versions: list[SchemaVersion] = field(default_factory=list)
    current_version: str = ""

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiGraphqlSchemaRegistry:
    def __init__(self) -> None:
        self._registries: dict[tuple[str, str], SchemaRegistry] = {}

    def create_registry(self, installation_id: str, registry_id: str, service_name: str) -> SchemaRegistry:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, registry_id)
        if key in self._registries: raise ValueError(f"Registry {registry_id} already exists")
        reg = SchemaRegistry(registry_id=registry_id, service_name=service_name)
        self._registries[key] = reg
        return reg

    def publish_version(self, installation_id: str, registry_id: str, version: str, schema_sdl: str, type_count: int = 0, query_count: int = 0, mutation_count: int = 0) -> SchemaVersion:
        reg = self._get(installation_id, registry_id)
        schema_hash = hashlib.sha256(schema_sdl.encode()).hexdigest()[:16]
        # Detect if same hash already published
        for v in reg.versions:
            if v.schema_hash == schema_hash and v.version != version:
                pass  # same schema, different version label is ok
        sv = SchemaVersion(version=version, schema_hash=schema_hash, type_count=type_count, query_count=query_count, mutation_count=mutation_count)
        reg.versions.append(sv)
        reg.current_version = version
        return sv

    def get_current(self, installation_id: str, registry_id: str) -> SchemaVersion | None:
        reg = self._get(installation_id, registry_id)
        if not reg.versions: return None
        return reg.versions[-1]

    def compare_versions(self, installation_id: str, registry_id: str, v1: str, v2: str) -> dict[str, object]:
        reg = self._get(installation_id, registry_id)
        sv1 = next((v for v in reg.versions if v.version == v1), None)
        sv2 = next((v for v in reg.versions if v.version == v2), None)
        if sv1 is None or sv2 is None: raise KeyError("Version not found")
        return {"schema_changed": sv1.schema_hash != sv2.schema_hash, "type_diff": sv2.type_count - sv1.type_count, "query_diff": sv2.query_count - sv1.query_count, "mutation_diff": sv2.mutation_count - sv1.mutation_count}

    def list_registries(self, installation_id: str) -> list[SchemaRegistry]:
        return [r for (inst, _), r in self._registries.items() if inst == installation_id]

    def _get(self, installation_id: str, registry_id: str) -> SchemaRegistry:
        r = self._registries.get((installation_id, registry_id))
        if r is None: raise KeyError(f"Registry {registry_id} not found")
        return r
