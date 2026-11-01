"""API Consumer Endpoint Response Schema — define expected response schemas."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class ResponseSchema:
    endpoint: str
    method: str
    status_code: int
    fields: dict[str, str] = field(default_factory=dict)
    required_fields: list[str] = field(default_factory=list)
    example: str = ""

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointResponseSchema:
    def __init__(self) -> None:
        self._schemas: dict[tuple[str, str, str, int], ResponseSchema] = {}

    def register(self, installation_id: str, schema: ResponseSchema) -> ResponseSchema:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, schema.method.upper(), schema.endpoint, schema.status_code)
        self._schemas[key] = schema
        return schema

    def validate(self, installation_id: str, method: str, endpoint: str, status_code: int, response: dict) -> list[str]:
        schema = self._schemas.get((installation_id, method.upper(), endpoint, status_code))
        if schema is None: return []
        errors: list[str] = []
        for rf in schema.required_fields:
            if rf not in response: errors.append(f"Missing: {rf}")
        TYPE_MAP = {"string": str, "int": int, "float": (int, float), "bool": bool, "list": list, "object": dict}
        for fname, ftype in schema.fields.items():
            if fname not in response: continue
            val = response[fname]
            if ftype in ("int", "float") and isinstance(val, bool):
                errors.append(f"{fname}: expected {ftype}, got bool")
            elif ftype in TYPE_MAP and not isinstance(val, TYPE_MAP[ftype]):
                errors.append(f"{fname}: expected {ftype}")
        return errors

    def get_schema(self, installation_id: str, method: str, endpoint: str, status_code: int) -> ResponseSchema | None:
        return self._schemas.get((installation_id, method.upper(), endpoint, status_code))

    def list_schemas(self, installation_id: str) -> list[ResponseSchema]:
        return [s for (inst, _, _, _), s in self._schemas.items() if inst == installation_id]
