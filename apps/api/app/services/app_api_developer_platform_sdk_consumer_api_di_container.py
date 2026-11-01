"""Consumer API Dependency Injection — service dependency container with lifecycle."""
from __future__ import annotations

import structlog
from dataclasses import dataclass, field

logger = structlog.get_logger()

LIFECYCLES = ("singleton", "transient", "scoped")


@dataclass
class ServiceRegistration:
    name: str
    factory: type | None = None
    instance: object | None = None
    lifecycle: str = "singleton"
    dependencies: list[str] = field(default_factory=list)


@dataclass
class DiContainer:
    """Lightweight dependency injection container."""

    _registrations: dict[str, ServiceRegistration] = field(default_factory=dict)
    _singletons: dict[str, object] = field(default_factory=dict)
    _resolution_stack: list[str] = field(default_factory=list)

    def register(self, name: str, factory: type | None = None, instance: object | None = None,
                 lifecycle: str = "singleton", dependencies: list[str] | None = None) -> dict:
        if name in self._registrations:
            raise ValueError(f"Service {name} already registered")
        if lifecycle not in LIFECYCLES:
            raise ValueError(f"Invalid lifecycle: {lifecycle}")
        if not factory and not instance:
            raise ValueError("Either factory or instance is required")
        self._registrations[name] = ServiceRegistration(
            name=name, factory=factory, instance=instance,
            lifecycle=lifecycle, dependencies=dependencies or [],
        )
        if instance:
            self._singletons[name] = instance
        logger.info("service_registered", name=name, lifecycle=lifecycle)
        return {"name": name, "lifecycle": lifecycle}

    def resolve(self, name: str) -> object:
        if name in self._resolution_stack:
            raise ValueError(f"Circular dependency detected: {' -> '.join(self._resolution_stack)} -> {name}")
        reg = self._registrations.get(name)
        if not reg:
            raise ValueError(f"Service {name} not registered")
        # Return existing singleton
        if reg.lifecycle == "singleton" and name in self._singletons:
            return self._singletons[name]
        # Return pre-set instance
        if reg.instance:
            return reg.instance
        # Build from factory
        self._resolution_stack.append(name)
        try:
            deps = {}
            for dep_name in reg.dependencies:
                deps[dep_name] = self.resolve(dep_name)
            instance = reg.factory(**deps) if deps else reg.factory()
            if reg.lifecycle == "singleton":
                self._singletons[name] = instance
            return instance
        finally:
            self._resolution_stack.pop()

    def has(self, name: str) -> bool:
        return name in self._registrations

    def get_registration(self, name: str) -> dict | None:
        reg = self._registrations.get(name)
        if not reg:
            return None
        return {
            "name": reg.name, "lifecycle": reg.lifecycle,
            "dependencies": reg.dependencies,
            "has_instance": reg.instance is not None or name in self._singletons,
        }

    def list_services(self) -> list[dict]:
        return [self.get_registration(n) for n in sorted(self._registrations)]

    def reset(self) -> dict:
        count = len(self._singletons)
        self._singletons.clear()
        return {"cleared_instances": count}

    def get_dependency_tree(self, name: str, depth: int = 0) -> dict:
        reg = self._registrations.get(name)
        if not reg:
            return {"name": name, "error": "not_found"}
        children = []
        for dep in reg.dependencies:
            children.append(self.get_dependency_tree(dep, depth + 1))
        return {"name": name, "lifecycle": reg.lifecycle,
                "depth": depth, "dependencies": children}

    def get_stats(self) -> dict:
        regs = list(self._registrations.values())
        return {
            "total_services": len(regs),
            "singletons": sum(1 for r in regs if r.lifecycle == "singleton"),
            "transient": sum(1 for r in regs if r.lifecycle == "transient"),
            "instantiated": len(self._singletons),
        }
