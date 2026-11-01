"""Dependency Graph — resolve and validate extension dependency trees.

Builds a DAG of extension dependencies, detects circular references,
computes install order via topological sort, and finds version conflicts.
"""
from __future__ import annotations
from collections import defaultdict, deque
from dataclasses import dataclass, field


@dataclass
class ExtDep:
    extension_id: str
    version: str
    dependencies: list[tuple[str, str]] = field(default_factory=list)  # (ext_id, version_req)


class DepGraphService:
    """Manages extension dependency graphs with cycle detection and topo sort."""

    def __init__(self):
        self._extensions: dict[str, ExtDep] = {}

    def register(self, extension_id: str, version: str,
                 dependencies: list[tuple[str, str]] | None = None) -> ExtDep:
        ext = ExtDep(extension_id=extension_id, version=version,
                     dependencies=dependencies or [])
        self._extensions[extension_id] = ext
        return ext

    def get_direct_deps(self, extension_id: str) -> list[tuple[str, str]]:
        ext = self._extensions.get(extension_id)
        return ext.dependencies if ext else []

    def get_all_deps(self, extension_id: str) -> set[str]:
        """Get transitive closure of all dependencies."""
        visited: set[str] = set()
        queue = deque([extension_id])
        while queue:
            current = queue.popleft()
            ext = self._extensions.get(current)
            if not ext:
                continue
            for dep_id, _ in ext.dependencies:
                if dep_id not in visited:
                    visited.add(dep_id)
                    queue.append(dep_id)
        return visited

    def detect_cycles(self, extension_id: str) -> list[str] | None:
        """Returns cycle path if circular dependency exists, None otherwise."""
        path: list[str] = []
        visited: set[str] = set()
        in_stack: set[str] = set()

        def dfs(node: str) -> list[str] | None:
            visited.add(node)
            in_stack.add(node)
            path.append(node)
            ext = self._extensions.get(node)
            if ext:
                for dep_id, _ in ext.dependencies:
                    if dep_id in in_stack:
                        cycle_start = path.index(dep_id)
                        return path[cycle_start:] + [dep_id]
                    if dep_id not in visited:
                        result = dfs(dep_id)
                        if result:
                            return result
            path.pop()
            in_stack.discard(node)
            return None

        return dfs(extension_id)

    def topological_sort(self, extension_id: str) -> list[str] | None:
        """Returns install order (deps first). None if cycle detected."""
        all_deps = self.get_all_deps(extension_id)
        all_deps.add(extension_id)

        in_degree: dict[str, int] = defaultdict(int)
        graph: dict[str, list[str]] = defaultdict(list)
        for eid in all_deps:
            ext = self._extensions.get(eid)
            if ext:
                for dep_id, _ in ext.dependencies:
                    if dep_id in all_deps:
                        graph[dep_id].append(eid)
                        in_degree[eid] += 1
                if eid not in in_degree:
                    in_degree[eid] = 0

        queue = deque([n for n in all_deps if in_degree.get(n, 0) == 0])
        result: list[str] = []
        while queue:
            node = queue.popleft()
            result.append(node)
            for neighbor in graph[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(result) != len(all_deps):
            return None  # cycle
        return result

    def find_conflicts(self, extension_ids: list[str]) -> list[dict]:
        """Find version conflicts across multiple extensions."""
        required: dict[str, list[tuple[str, str]]] = defaultdict(list)
        for eid in extension_ids:
            ext = self._extensions.get(eid)
            if ext:
                for dep_id, ver_req in ext.dependencies:
                    required[dep_id].append((eid, ver_req))
        conflicts = []
        for dep_id, requesters in required.items():
            versions = {v for _, v in requesters}
            if len(versions) > 1:
                conflicts.append({
                    "dependency": dep_id,
                    "requested_by": requesters,
                    "versions": sorted(versions),
                })
        return conflicts

    def get_dependents(self, extension_id: str) -> list[str]:
        """Find all extensions that depend on the given one."""
        return [eid for eid, ext in self._extensions.items()
                if any(d == extension_id for d, _ in ext.dependencies)]
