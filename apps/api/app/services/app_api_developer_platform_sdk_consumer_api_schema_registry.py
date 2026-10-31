"""Consumer API Schema Registry — API schema versioning with validation."""
from __future__ import annotations

import structlog
from dataclasses import dataclass, field

logger = structlog.get_logger()


@dataclass
class SchemaField:
    name: str
    field_type: str  # string, int, float, bool, array, object
    required: bool = True
    description: str = ""


@dataclass
class Schema:
    schema_id: str
    endpoint_id: str
    version: str
    fields: list[SchemaField]
    direction: str = "response"  # request, response


@dataclass
class SchemaRegistry:
    """Registry for API schemas with versioning and compatibility checks."""

    _schemas: dict[str, Schema] = field(default_factory=dict)  # schema_id -> schema

    def register(self, schema: Schema) -> dict:
        if schema.schema_id in self._schemas:
            raise ValueError(f"Schema {schema.schema_id} already registered")
        if not schema.fields:
            raise ValueError("Schema must have at least one field")
        self._schemas[schema.schema_id] = schema
        logger.info("schema_registered", schema_id=schema.schema_id)
        return {"schema_id": schema.schema_id, "version": schema.version,
                "field_count": len(schema.fields)}

    def get_schema(self, schema_id: str) -> dict | None:
        s = self._schemas.get(schema_id)
        if not s:
            return None
        return {
            "schema_id": s.schema_id, "endpoint_id": s.endpoint_id,
            "version": s.version, "direction": s.direction,
            "fields": [{"name": f.name, "type": f.field_type,
                        "required": f.required} for f in s.fields],
        }

    def validate(self, schema_id: str, data: dict) -> dict:
        schema = self._schemas.get(schema_id)
        if not schema:
            raise ValueError(f"Schema {schema_id} not found")
        errors = []
        type_map = {"string": str, "int": int, "float": (int, float),
                     "bool": bool, "array": list, "object": dict}
        for f in schema.fields:
            if f.name not in data:
                if f.required:
                    errors.append({"field": f.name, "error": "missing"})
                continue
            val = data[f.name]
            if val is not None:
                expected = type_map.get(f.field_type)
                if expected and f.field_type == "int" and isinstance(val, bool):
                    errors.append({"field": f.name, "error": "type_mismatch"})
                elif expected and not isinstance(val, expected):
                    errors.append({"field": f.name, "error": "type_mismatch",
                                   "expected": f.field_type})
        return {"valid": len(errors) == 0, "errors": errors, "checked": len(schema.fields)}

    def check_compatibility(self, schema_id_a: str, schema_id_b: str) -> dict:
        a = self._schemas.get(schema_id_a)
        b = self._schemas.get(schema_id_b)
        if not a or not b:
            raise ValueError("Both schemas must exist")
        fields_a = {f.name for f in a.fields}
        fields_b = {f.name for f in b.fields}
        added = sorted(fields_b - fields_a)
        removed = sorted(fields_a - fields_b)
        breaking = len(removed) > 0
        return {"from": schema_id_a, "to": schema_id_b,
                "added": added, "removed": removed,
                "compatible": not breaking}

    def get_versions(self, endpoint_id: str) -> list[dict]:
        schemas = [s for s in self._schemas.values() if s.endpoint_id == endpoint_id]
        schemas.sort(key=lambda s: s.version, reverse=True)
        return [{"schema_id": s.schema_id, "version": s.version,
                 "direction": s.direction, "fields": len(s.fields)}
                for s in schemas]

    def get_latest(self, endpoint_id: str, direction: str = "response") -> dict | None:
        schemas = [s for s in self._schemas.values()
                   if s.endpoint_id == endpoint_id and s.direction == direction]
        if not schemas:
            return None
        latest = max(schemas, key=lambda s: s.version)
        return self.get_schema(latest.schema_id)

    def get_stats(self) -> dict:
        schemas = list(self._schemas.values())
        endpoints = set(s.endpoint_id for s in schemas)
        return {
            "total_schemas": len(schemas),
            "unique_endpoints": len(endpoints),
            "request_schemas": sum(1 for s in schemas if s.direction == "request"),
            "response_schemas": sum(1 for s in schemas if s.direction == "response"),
        }
