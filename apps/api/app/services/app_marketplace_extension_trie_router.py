"""Trie-based Router — fast URL routing with path parameters and wildcards.

Implements:
- Radix trie for O(path-length) route matching
- Path parameters (:id) and wildcard (*path) capture
- Method-based routing (GET, POST, etc.)
- Route conflict detection
- Middleware chain per route
"""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class RouteMatch:
    handler: str
    params: dict[str, str]
    method: str
    path: str
    middleware: list[str]


@dataclass
class TrieNode:
    children: dict[str, TrieNode] = field(default_factory=dict)
    param_child: TrieNode | None = None
    param_name: str = ""
    wildcard_child: TrieNode | None = None
    wildcard_name: str = ""
    handlers: dict[str, str] = field(default_factory=dict)  # method -> handler
    middleware: list[str] = field(default_factory=list)


class TrieRouterService:
    def __init__(self):
        self._root = TrieNode()
        self._routes: list[dict] = []

    def add(self, method: str, path: str, handler: str,
            middleware: list[str] | None = None) -> None:
        parts = [p for p in path.strip("/").split("/") if p]
        node = self._root

        for part in parts:
            if part.startswith(":"):
                # Path parameter
                if node.param_child is None:
                    node.param_child = TrieNode()
                    node.param_name = part[1:]
                elif node.param_name != part[1:]:
                    raise ValueError(f"Conflicting param names: :{node.param_name} vs :{part[1:]}")
                node = node.param_child
            elif part.startswith("*"):
                # Wildcard (catch-all, must be last)
                if node.wildcard_child is None:
                    node.wildcard_child = TrieNode()
                    node.wildcard_name = part[1:] or "wildcard"
                node = node.wildcard_child
                break
            else:
                if part not in node.children:
                    node.children[part] = TrieNode()
                node = node.children[part]

        if method in node.handlers:
            raise ValueError(f"Route conflict: {method} {path}")
        node.handlers[method] = handler
        node.middleware = middleware or []
        self._routes.append({"method": method, "path": path, "handler": handler})

    def match(self, method: str, path: str) -> RouteMatch | None:
        parts = [p for p in path.strip("/").split("/") if p]
        params: dict[str, str] = {}
        result = self._match_node(self._root, parts, 0, params)

        if result is None:
            return None

        node, captured_params = result
        handler = node.handlers.get(method) or node.handlers.get("ANY")
        if not handler:
            return None

        return RouteMatch(handler=handler, params=captured_params,
                          method=method, path=path, middleware=node.middleware)

    def _match_node(self, node: TrieNode, parts: list[str], idx: int,
                    params: dict[str, str]) -> tuple[TrieNode, dict] | None:
        if idx == len(parts):
            if node.handlers:
                return node, dict(params)
            return None

        part = parts[idx]

        # 1. Exact match (highest priority)
        if part in node.children:
            result = self._match_node(node.children[part], parts, idx + 1, params)
            if result:
                return result

        # 2. Parameter match
        if node.param_child is not None:
            params[node.param_name] = part
            result = self._match_node(node.param_child, parts, idx + 1, params)
            if result:
                return result
            del params[node.param_name]

        # 3. Wildcard match (lowest priority, captures rest)
        if node.wildcard_child is not None:
            params[node.wildcard_name] = "/".join(parts[idx:])
            if node.wildcard_child.handlers:
                return node.wildcard_child, dict(params)

        return None

    def get_routes(self) -> list[dict]:
        return list(self._routes)

    def route_count(self) -> int:
        return len(self._routes)
