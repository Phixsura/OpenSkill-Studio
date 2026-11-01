"""Dependency Injection Container — IoC with lifecycle management.

Implements:
- Register services as singletons, transient, or scoped
- Constructor injection via factory functions
- Lazy resolution (create on first request)
- Circular dependency detection
- Named registrations for multiple implementations
- Scope management for request-scoped services
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum


class Lifecycle(str, Enum):
    SINGLETON = "singleton"  # one instance ever
    TRANSIENT = "transient"  # new instance every request
    SCOPED = "scoped"        # one instance per scope


@dataclass
class Registration:
    name: str
    factory: callable
    lifecycle: Lifecycle
    dependencies: list[str] = field(default_factory=list)
    instance: object | None = None
    resolved_count: int = 0


class DiContainerService:
    def __init__(self):
        self._registrations: dict[str, Registration] = {}
        self._scopes: dict[str, dict[str, object]] = {}  # scope_id -> {name -> instance}
        self._resolving: set[str] = set()  # for circular detection

    def register(self, name: str, factory: callable,
                 lifecycle: Lifecycle = Lifecycle.SINGLETON,
                 dependencies: list[str] | None = None) -> None:
        self._registrations[name] = Registration(
            name=name, factory=factory, lifecycle=lifecycle,
            dependencies=dependencies or [])

    def register_instance(self, name: str, instance: object) -> None:
        """Register a pre-built instance as singleton."""
        reg = Registration(name=name, factory=lambda: instance,
                           lifecycle=Lifecycle.SINGLETON, instance=instance)
        self._registrations[name] = reg

    def resolve(self, name: str, scope_id: str = "") -> object:
        """Resolve a service by name. Creates instance if needed."""
        reg = self._registrations.get(name)
        if not reg:
            raise ValueError(f"Service '{name}' not registered")

        # Circular dependency detection
        if name in self._resolving:
            raise ValueError(f"Circular dependency detected: {name}")

        # Singleton: return cached
        if reg.lifecycle == Lifecycle.SINGLETON and reg.instance is not None:
            reg.resolved_count += 1
            return reg.instance

        # Scoped: return from scope cache
        if reg.lifecycle == Lifecycle.SCOPED and scope_id:
            scope = self._scopes.get(scope_id, {})
            if name in scope:
                reg.resolved_count += 1
                return scope[name]

        # Resolve dependencies first
        self._resolving.add(name)
        try:
            deps = []
            for dep_name in reg.dependencies:
                deps.append(self.resolve(dep_name, scope_id))

            # Create instance
            instance = reg.factory(*deps) if deps else reg.factory()
            reg.resolved_count += 1
        finally:
            self._resolving.discard(name)

        # Cache based on lifecycle
        if reg.lifecycle == Lifecycle.SINGLETON:
            reg.instance = instance
        elif reg.lifecycle == Lifecycle.SCOPED and scope_id:
            if scope_id not in self._scopes:
                self._scopes[scope_id] = {}
            self._scopes[scope_id][name] = instance

        return instance

    def create_scope(self, scope_id: str) -> str:
        """Create a new resolution scope."""
        self._scopes[scope_id] = {}
        return scope_id

    def dispose_scope(self, scope_id: str) -> int:
        """Dispose a scope and its instances. Returns count disposed."""
        scope = self._scopes.pop(scope_id, {})
        return len(scope)

    def is_registered(self, name: str) -> bool:
        return name in self._registrations

    def get_registrations(self) -> list[dict]:
        return [{"name": r.name, "lifecycle": r.lifecycle.value,
                 "dependencies": r.dependencies, "resolved_count": r.resolved_count}
                for r in self._registrations.values()]
