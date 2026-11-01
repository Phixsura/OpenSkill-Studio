"""Consumer API GraphQL Schema — manage GraphQL type definitions and field access."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class GraphQLField:
    name: str
    field_type: str  # "String", "Int", "Float", "Boolean", "ID", "[Type]"
    nullable: bool = True
    deprecated: bool = False
    deprecation_reason: str = ""

@dataclass
class GraphQLType:
    type_name: str
    kind: str = "object"  # "object", "input", "enum", "interface"
    fields: list[GraphQLField] = field(default_factory=list)
    description: str = ""

@dataclass
class FieldAccessRule:
    type_name: str
    field_name: str
    consumer_id: str
    allowed: bool = True

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiGraphqlSchema:
    def __init__(self) -> None:
        self._types: dict[tuple[str, str], GraphQLType] = {}  # (inst, type_name)
        self._access: dict[tuple[str, str, str, str], FieldAccessRule] = {}  # (inst, consumer, type, field)

    def register_type(self, installation_id: str, gql_type: GraphQLType) -> GraphQLType:
        if not installation_id:
            raise ValueError("installation_id is required")
        if gql_type.kind not in ("object", "input", "enum", "interface"):
            raise ValueError(f"Invalid kind: {gql_type.kind}")
        self._types[(installation_id, gql_type.type_name)] = gql_type
        log.info("graphql_type_registered", installation_id=installation_id, type=gql_type.type_name, fields=len(gql_type.fields))
        return gql_type

    def get_type(self, installation_id: str, type_name: str) -> GraphQLType | None:
        return self._types.get((installation_id, type_name))

    def set_field_access(self, installation_id: str, rule: FieldAccessRule) -> FieldAccessRule:
        self._access[(installation_id, rule.consumer_id, rule.type_name, rule.field_name)] = rule
        return rule

    def get_visible_fields(self, installation_id: str, consumer_id: str, type_name: str) -> list[GraphQLField]:
        gql_type = self._types.get((installation_id, type_name))
        if not gql_type:
            return []
        result = []
        for f in gql_type.fields:
            rule = self._access.get((installation_id, consumer_id, type_name, f.name))
            if rule and not rule.allowed:
                continue
            result.append(f)
        return result

    def introspect(self, installation_id: str) -> list[GraphQLType]:
        return sorted([t for (inst, _), t in self._types.items() if inst == installation_id], key=lambda t: t.type_name)
