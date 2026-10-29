"""App API Developer GraphQL Query Analyzer — analyze query complexity and depth."""
from __future__ import annotations
from dataclasses import dataclass, field
import re
import structlog

log = structlog.get_logger()

@dataclass
class QueryAnalysis:
    query_id: str
    depth: int
    field_count: int
    estimated_cost: int
    has_introspection: bool = False
    warnings: list[str] = field(default_factory=list)

class AppAPIDeveloperAPIGraphQLQueryAnalyzer:
    def __init__(self, max_depth: int = 10, max_cost: int = 1000) -> None:
        self._max_depth = max_depth
        self._max_cost = max_cost
        self._analyses: dict[str, list[QueryAnalysis]] = {}

    def analyze(self, installation_id: str, query_id: str, query: str) -> QueryAnalysis:
        if not installation_id: raise ValueError("installation_id is required")
        depth = self._calc_depth(query)
        field_count = len(re.findall(r'\w+\s*[({:]', query))
        cost = field_count * max(1, depth)
        has_introspection = "__schema" in query or "__type" in query
        warnings: list[str] = []
        if depth > self._max_depth: warnings.append(f"Depth {depth} exceeds max {self._max_depth}")
        if cost > self._max_cost: warnings.append(f"Cost {cost} exceeds max {self._max_cost}")
        if has_introspection: warnings.append("Contains introspection query")
        a = QueryAnalysis(query_id=query_id, depth=depth, field_count=field_count, estimated_cost=cost, has_introspection=has_introspection, warnings=warnings)
        self._analyses.setdefault(installation_id, []).append(a)
        return a

    def recent(self, installation_id: str, limit: int = 20) -> list[QueryAnalysis]:
        return list(reversed(self._analyses.get(installation_id, [])[-limit:]))

    def expensive_queries(self, installation_id: str, threshold: int = 500) -> list[QueryAnalysis]:
        return [a for a in self._analyses.get(installation_id, []) if a.estimated_cost >= threshold]

    def _calc_depth(self, query: str) -> int:
        max_d = current = 0
        for ch in query:
            if ch == '{': current += 1; max_d = max(max_d, current)
            elif ch == '}': current = max(0, current - 1)
        return max_d
