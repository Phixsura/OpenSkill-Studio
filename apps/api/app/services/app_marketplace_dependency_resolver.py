"""Dependency Resolver — resolve extension dependencies with cycle detection.

Extensions can depend on other extensions. This service resolves
the full dependency tree, detects cycles, and computes install order.
"""
from __future__ import annotations
from collections import defaultdict


class DependencyError(Exception):
    pass


class CyclicDependencyError(DependencyError):
    def __init__(self, cycle: list[str]):
        self.cycle = cycle
        super().__init__(f"Cyclic dependency: {' -> '.join(cycle)}")


class MissingDependencyError(DependencyError):
    def __init__(self, extension_id: str, missing: str):
        self.extension_id = extension_id
        self.missing = missing
        super().__init__(f"{extension_id} depends on unknown {missing}")


class DependencyResolver:
    """Resolves extension dependency graphs with topological sort."""

    def __init__(self):
        self._deps: dict[str, list[str]] = defaultdict(list)
        self._registered: set[str] = set()

    def register(self, extension_id: str, dependencies: list[str] | None = None) -> None:
        """Register an extension with its dependencies."""
        self._registered.add(extension_id)
        self._deps[extension_id] = dependencies or []

    def get_dependencies(self, extension_id: str) -> list[str]:
        """Get direct dependencies of an extension."""
        return list(self._deps.get(extension_id, []))

    def resolve(self, extension_id: str) -> list[str]:
        """Resolve full install order (topological sort). Raises on cycles."""
        if extension_id not in self._registered:
            raise MissingDependencyError(extension_id, extension_id)

        visited: set[str] = set()
        in_stack: set[str] = set()
        order: list[str] = []

        def dfs(node: str, path: list[str]) -> None:
            if node in in_stack:
                cycle_start = path.index(node)
                raise CyclicDependencyError(path[cycle_start:] + [node])
            if node in visited:
                return
            in_stack.add(node)
            path.append(node)
            for dep in self._deps.get(node, []):
                if dep not in self._registered:
                    raise MissingDependencyError(node, dep)
                dfs(dep, path)
            path.pop()
            in_stack.remove(node)
            visited.add(node)
            order.append(node)

        dfs(extension_id, [])
        return order  # install order: dependencies first, target last

    def resolve_all(self, extension_ids: list[str]) -> list[str]:
        """Resolve install order for multiple extensions."""
        all_ordered: list[str] = []
        seen: set[str] = set()
        for ext_id in extension_ids:
            for item in self.resolve(ext_id):
                if item not in seen:
                    all_ordered.append(item)
                    seen.add(item)
        return all_ordered

    def check_conflicts(self, ext_a: str, ext_b: str) -> bool:
        """Check if two extensions have conflicting dependency trees."""
        try:
            deps_a = set(self.resolve(ext_a))
            deps_b = set(self.resolve(ext_b))
            # Simple conflict: both depend on each other indirectly
            return ext_a in deps_b or ext_b in deps_a
        except DependencyError:
            return True

    def get_dependents(self, extension_id: str) -> list[str]:
        """Find all extensions that depend on a given extension."""
        return [
            ext for ext, deps in self._deps.items()
            if extension_id in deps
        ]
