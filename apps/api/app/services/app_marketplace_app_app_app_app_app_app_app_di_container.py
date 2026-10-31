"""Dependency injection container — register and resolve service dependencies."""
from __future__ import annotations


class DIContainer:
    def __init__(self):
        self._registry: dict[str, dict] = {}
        self._singletons: dict[str, object] = {}

    def register(self, name: str, factory: callable, singleton: bool = False) -> dict:
        self._registry[name] = {"factory": factory, "singleton": singleton}
        return {"name": name, "singleton": singleton, "registered": True}

    def resolve(self, name: str) -> object:
        if name not in self._registry:
            raise KeyError(f"Service '{name}' not registered")
        entry = self._registry[name]
        if entry["singleton"]:
            if name not in self._singletons:
                self._singletons[name] = entry["factory"]()
            return self._singletons[name]
        return entry["factory"]()

    def has(self, name: str) -> bool:
        return name in self._registry

    def stats(self) -> dict:
        return {"registered": len(self._registry),
                "singletons_created": len(self._singletons),
                "services": sorted(self._registry.keys())}
