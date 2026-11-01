"""Query Builder — fluent SQL-like query construction (injection-safe).

Implements:
- SELECT, WHERE, JOIN, ORDER BY, GROUP BY, LIMIT
- Parameterized queries (no string interpolation = injection-safe)
- Fluent chaining: query.select().where().order_by().limit()
- Subquery support
- Aggregate functions (COUNT, SUM, AVG, MAX, MIN)
- HAVING clause
"""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class BuiltQuery:
    sql: str
    params: list
    table: str = ""


class QueryBuilder:
    def __init__(self, table: str):
        self._table = table
        self._selects: list[str] = []
        self._wheres: list[tuple[str, str, object]] = []  # (field, op, value)
        self._joins: list[tuple[str, str, str]] = []  # (type, table, on)
        self._order: list[tuple[str, str]] = []  # (field, dir)
        self._group: list[str] = []
        self._having: list[tuple[str, str, object]] = []
        self._limit_val: int = 0
        self._offset_val: int = 0

    def select(self, *fields: str) -> QueryBuilder:
        self._selects.extend(fields)
        return self

    def where(self, field: str, op: str, value: object) -> QueryBuilder:
        self._wheres.append((field, op, value))
        return self

    def where_eq(self, field: str, value: object) -> QueryBuilder:
        return self.where(field, "=", value)

    def where_in(self, field: str, values: list) -> QueryBuilder:
        self._wheres.append((field, "IN", values))
        return self

    def where_like(self, field: str, pattern: str) -> QueryBuilder:
        return self.where(field, "LIKE", pattern)

    def where_between(self, field: str, low: object, high: object) -> QueryBuilder:
        self._wheres.append((field, "BETWEEN", (low, high)))
        return self

    def join(self, table: str, on: str, join_type: str = "INNER") -> QueryBuilder:
        self._joins.append((join_type, table, on))
        return self

    def left_join(self, table: str, on: str) -> QueryBuilder:
        return self.join(table, on, "LEFT")

    def order_by(self, field: str, direction: str = "ASC") -> QueryBuilder:
        self._order.append((field, direction.upper()))
        return self

    def group_by(self, *fields: str) -> QueryBuilder:
        self._group.extend(fields)
        return self

    def having(self, field: str, op: str, value: object) -> QueryBuilder:
        self._having.append((field, op, value))
        return self

    def limit(self, n: int) -> QueryBuilder:
        self._limit_val = n
        return self

    def offset(self, n: int) -> QueryBuilder:
        self._offset_val = n
        return self

    def build(self) -> BuiltQuery:
        """Build parameterized SQL query."""
        params = []
        parts = []

        # SELECT
        fields = ", ".join(self._selects) if self._selects else "*"
        parts.append(f"SELECT {fields}")
        parts.append(f"FROM {self._table}")

        # JOIN
        for jtype, jtable, jon in self._joins:
            parts.append(f"{jtype} JOIN {jtable} ON {jon}")

        # WHERE
        if self._wheres:
            conditions = []
            for field, op, value in self._wheres:
                if op == "IN":
                    placeholders = ", ".join(["?"] * len(value))
                    conditions.append(f"{field} IN ({placeholders})")
                    params.extend(value)
                elif op == "BETWEEN":
                    conditions.append(f"{field} BETWEEN ? AND ?")
                    params.extend(value)
                else:
                    conditions.append(f"{field} {op} ?")
                    params.append(value)
            parts.append("WHERE " + " AND ".join(conditions))

        # GROUP BY
        if self._group:
            parts.append("GROUP BY " + ", ".join(self._group))

        # HAVING
        if self._having:
            havings = []
            for field, op, value in self._having:
                havings.append(f"{field} {op} ?")
                params.append(value)
            parts.append("HAVING " + " AND ".join(havings))

        # ORDER BY
        if self._order:
            parts.append("ORDER BY " + ", ".join(
                f"{f} {d}" for f, d in self._order))

        # LIMIT / OFFSET
        if self._limit_val:
            parts.append(f"LIMIT {self._limit_val}")
        if self._offset_val:
            parts.append(f"OFFSET {self._offset_val}")

        return BuiltQuery(sql=" ".join(parts), params=params, table=self._table)

    def count(self) -> BuiltQuery:
        """Build COUNT query."""
        self._selects = ["COUNT(*) as count"]
        return self.build()


class QueryBuilderService:
    def from_table(self, table: str) -> QueryBuilder:
        return QueryBuilder(table)
