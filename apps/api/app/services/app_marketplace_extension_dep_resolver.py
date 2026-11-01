"""Extension Dependency Resolver — resolve and validate extension dependencies."""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class ExtDep:
    extension_id: str
    version: str
    optional: bool = False


@dataclass
class ExtManifest:
    extension_id: str
    version: str
    dependencies: list[ExtDep] = field(default_factory=list)


class ExtDepResolverService:
    def __init__(self):
        self._registry: dict[str, ExtManifest] = {}

    def register(self, extension_id: str, version: str,
                 deps: list[tuple[str, str, bool]] | None = None) -> ExtManifest:
        dep_list = [ExtDep(d[0], d[1], d[2] if len(d) > 2 else False)
                    for d in (deps or [])]
        m = ExtManifest(extension_id=extension_id, version=version, dependencies=dep_list)
        self._registry[extension_id] = m
        return m

    def resolve(self, extension_id: str) -> tuple[list[str], list[str]]:
        """Returns (resolved_order, missing)."""
        resolved: list[str] = []
        missing: list[str] = []
        visited: set[str] = set()

        def _visit(eid: str):
            if eid in visited:
                return
            visited.add(eid)
            m = self._registry.get(eid)
            if not m:
                missing.append(eid)
                return
            for dep in m.dependencies:
                _visit(dep.extension_id)
            resolved.append(eid)

        _visit(extension_id)
        return resolved, missing

    def check_circular(self, extension_id: str) -> list[str] | None:
        """Returns circular chain if found, else None."""
        path: list[str] = []
        visiting: set[str] = set()

        def _visit(eid: str) -> list[str] | None:
            if eid in visiting:
                cycle_start = path.index(eid)
                return path[cycle_start:] + [eid]
            visiting.add(eid)
            path.append(eid)
            m = self._registry.get(eid)
            if m:
                for dep in m.dependencies:
                    result = _visit(dep.extension_id)
                    if result:
                        return result
            path.pop()
            visiting.discard(eid)
            return None

        return _visit(extension_id)

    def get_dependents(self, extension_id: str) -> list[str]:
        return [eid for eid, m in self._registry.items()
                if any(d.extension_id == extension_id for d in m.dependencies)]
