"""App API GraphQL Schema — manage GraphQL type definitions.

Manages GraphQL schemas:
- Register types with fields
- Track query/mutation operations
- Schema statistics
- Per-installation scoped schemas
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class GraphQLType:
    """A GraphQL type definition."""

    type_name: str
    kind: str  # "type", "input", "enum", "interface"
    fields: list[str] = field(default_factory=list)


@dataclass
class GraphQLOperation:
    """A GraphQL query or mutation."""

    name: str
    operation_type: str  # "query", "mutation", "subscription"
    return_type: str


class AppAPIGraphQLSchema:
    """Manage GraphQL type definitions."""

    def __init__(self) -> None:
        self._types: dict[tuple[str, str], GraphQLType] = {}
        self._operations: dict[tuple[str, str], GraphQLOperation] = {}

    def register_type(
        self, installation_id: str, type_name: str, kind: str, fields: list[str],
    ) -> GraphQLType:
        if not installation_id:
            raise ValueError("installation_id is required")
        if kind not in ("type", "input", "enum", "interface"):
            raise ValueError("kind must be type, input, enum, or interface")

        t = GraphQLType(type_name=type_name, kind=kind, fields=fields)
        self._types[(installation_id, type_name)] = t
        return t

    def register_operation(
        self, installation_id: str, name: str, operation_type: str, return_type: str,
    ) -> GraphQLOperation:
        if operation_type not in ("query", "mutation", "subscription"):
            raise ValueError("operation_type must be query, mutation, or subscription")

        op = GraphQLOperation(name=name, operation_type=operation_type, return_type=return_type)
        self._operations[(installation_id, name)] = op
        return op

    def schema_stats(self, installation_id: str) -> dict:
        types = [t for (inst, _), t in self._types.items() if inst == installation_id]
        ops = [o for (inst, _), o in self._operations.items() if inst == installation_id]
        return {
            "types": len(types),
            "fields": sum(len(t.fields) for t in types),
            "queries": sum(1 for o in ops if o.operation_type == "query"),
            "mutations": sum(1 for o in ops if o.operation_type == "mutation"),
        }

    def list_types(self, installation_id: str) -> list[GraphQLType]:
        return [t for (inst, _), t in self._types.items() if inst == installation_id]

    def list_operations(self, installation_id: str) -> list[GraphQLOperation]:
        return [o for (inst, _), o in self._operations.items() if inst == installation_id]
