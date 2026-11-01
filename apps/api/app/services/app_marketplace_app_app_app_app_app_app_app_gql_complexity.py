"""GraphQL query complexity analyzer — estimate cost before execution."""
from __future__ import annotations
import re

DEFAULT_FIELD_COST = 1
LIST_MULTIPLIER = 10


def analyze_complexity(query: str, *, max_complexity: int = 1000,
                        max_depth: int = 10) -> dict:
    depth = _max_depth(query)
    fields = len(re.findall(r"\w+\s*[({]", query)) + len(re.findall(r"\w+(?=\s*\n|\s*})", query))
    lists = len(re.findall(r"\b(edges|nodes|items|list|all)\b", query, re.IGNORECASE))
    complexity = fields * DEFAULT_FIELD_COST + lists * LIST_MULTIPLIER
    allowed = complexity <= max_complexity and depth <= max_depth
    return {
        "complexity": complexity, "max_complexity": max_complexity,
        "depth": depth, "max_depth": max_depth,
        "fields": fields, "lists": lists,
        "allowed": allowed,
        "reason": None if allowed else "complexity_exceeded" if complexity > max_complexity else "depth_exceeded",
    }


def _max_depth(query: str) -> int:
    max_d = 0
    current = 0
    for ch in query:
        if ch == "{":
            current += 1
            max_d = max(max_d, current)
        elif ch == "}":
            current -= 1
    return max_d
