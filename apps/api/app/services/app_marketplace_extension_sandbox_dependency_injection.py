"""Sandbox Dependency Injection — IoC container for extension sandboxes.

Manages service registration with singleton/transient/scoped lifetimes,
constructor injection, interface-based resolution, and dependency graphs.
"""
from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum


class Lifetime(str, Enum):
    SINGLETON = "singleton"
    TRANSIENT = "transient"
    SCOPED = "scoped"


@dataclass
class ServiceRegistration:
    name: str
    implementation: str
    lifetime: Lifetime = Lifetime.SINGLETON
    dependencies: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)


@dataclass
class ResolvedService:
    name: str
    implementation: str
    instance_id: int
    from_cache: bool = False


class SandboxDependencyInjectionService:
    """IoC container with lifetime management and dependency resolution."""

    def __init__(self):
        self._registrations: dict[str, dict[str, ServiceRegistration]] = defaultdict(dict)
        self._singletons: dict[str, dict[str, ResolvedService]] = defaultdict(dict)
        self._instance_counter: int = 0

    def register(self, sandbox_id: str, name: str, implementation: str,
                 lifetime: Lifetime = Lifetime.SINGLETON,
                 dependencies: list[str] | None = None,
                 tags: list[str] | None = None) -> ServiceRegistration:
        reg = ServiceRegistration(
            name=name, implementation=implementation,
            lifetime=lifetime, dependencies=dependencies or [],
            tags=tags or [],
        )
        self._registrations[sandbox_id][name] = reg
        return reg

    def resolve(self, sandbox_id: str, name: str) -> ResolvedService | dict:
        reg = self._registrations.get(sandbox_id, {}).get(name)
        if not reg:
            return {"error": f"Service '{name}' not registered"}

        # Check for circular dependencies
        cycle = self._detect_cycle(sandbox_id, name, set())
        if cycle:
            return {"error": f"Circular dependency: {' → '.join(cycle)}"}

        # Resolve dependencies first
        for dep_name in reg.dependencies:
            dep_result = self.resolve(sandbox_id, dep_name)
            if isinstance(dep_result, dict) and "error" in dep_result:
                return dep_result

        if reg.lifetime == Lifetime.SINGLETON:
            if name in self._singletons.get(sandbox_id, {}):
                cached = self._singletons[sandbox_id][name]
                cached.from_cache = True
                return cached

        self._instance_counter += 1
        resolved = ResolvedService(
            name=name, implementation=reg.implementation,
            instance_id=self._instance_counter,
        )

        if reg.lifetime == Lifetime.SINGLETON:
            self._singletons.setdefault(sandbox_id, {})[name] = resolved

        return resolved

    def _detect_cycle(self, sandbox_id: str, name: str,
                      visited: set[str]) -> list[str] | None:
        if name in visited:
            return [name]
        visited.add(name)
        reg = self._registrations.get(sandbox_id, {}).get(name)
        if reg:
            for dep in reg.dependencies:
                cycle = self._detect_cycle(sandbox_id, dep, visited.copy())
                if cycle:
                    return [name] + cycle
        return None

    def get_dependency_graph(self, sandbox_id: str) -> dict[str, list[str]]:
        graph: dict[str, list[str]] = {}
        for name, reg in self._registrations.get(sandbox_id, {}).items():
            graph[name] = reg.dependencies
        return graph

    def find_by_tag(self, sandbox_id: str, tag: str) -> list[str]:
        return [name for name, reg in self._registrations.get(sandbox_id, {}).items()
                if tag in reg.tags]

    def list_services(self, sandbox_id: str) -> list[dict]:
        return [
            {"name": r.name, "implementation": r.implementation,
             "lifetime": r.lifetime.value, "deps": r.dependencies}
            for r in self._registrations.get(sandbox_id, {}).values()
        ]

    def clear(self, sandbox_id: str) -> int:
        count = len(self._registrations.get(sandbox_id, {}))
        self._registrations[sandbox_id] = {}
        self._singletons[sandbox_id] = {}
        return count
