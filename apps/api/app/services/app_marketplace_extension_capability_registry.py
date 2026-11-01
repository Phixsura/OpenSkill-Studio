"""Capability Registry — declare and check extension capabilities.

Extensions declare capabilities they provide (e.g. "chart", "export",
"auth"), consumers check for required capabilities, and the registry
enables capability-based discovery and matching.
"""
from __future__ import annotations
import secrets
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class Capability:
    name: str
    version: str = "1.0"
    description: str = ""
    required_permissions: list[str] = field(default_factory=list)


@dataclass
class ExtensionCapabilities:
    extension_id: str
    provides: list[Capability] = field(default_factory=list)
    requires: list[str] = field(default_factory=list)


class CapabilityRegistryService:
    """Manages capability declarations for extensions."""

    def __init__(self):
        self._registry: dict[str, ExtensionCapabilities] = {}
        self._capability_index: dict[str, set[str]] = defaultdict(set)

    def declare(self, extension_id: str, provides: list[dict],
                requires: list[str] | None = None) -> ExtensionCapabilities:
        caps = [Capability(
            name=c["name"], version=c.get("version", "1.0"),
            description=c.get("description", ""),
            required_permissions=c.get("permissions", []),
        ) for c in provides]

        entry = ExtensionCapabilities(
            extension_id=extension_id, provides=caps,
            requires=requires or [],
        )
        self._registry[extension_id] = entry

        for cap in caps:
            self._capability_index[cap.name].add(extension_id)

        return entry

    def has_capability(self, extension_id: str, capability: str) -> bool:
        entry = self._registry.get(extension_id)
        if not entry:
            return False
        return any(c.name == capability for c in entry.provides)

    def find_providers(self, capability: str) -> list[str]:
        return sorted(self._capability_index.get(capability, set()))

    def check_requirements(self, extension_id: str) -> dict:
        entry = self._registry.get(extension_id)
        if not entry:
            return {"satisfied": True, "missing": []}

        missing = []
        for req in entry.requires:
            providers = self.find_providers(req)
            if not providers:
                missing.append(req)

        return {
            "satisfied": len(missing) == 0,
            "missing": missing,
            "requirements": entry.requires,
        }

    def get_capabilities(self, extension_id: str) -> list[dict]:
        entry = self._registry.get(extension_id)
        if not entry:
            return []
        return [{"name": c.name, "version": c.version,
                 "description": c.description}
                for c in entry.provides]

    def find_compatible(self, required_capabilities: list[str]) -> list[str]:
        """Find extensions that provide ALL required capabilities."""
        if not required_capabilities:
            return sorted(self._registry.keys())
        sets = [self._capability_index.get(cap, set()) for cap in required_capabilities]
        if not sets:
            return []
        result = sets[0]
        for s in sets[1:]:
            result = result & s
        return sorted(result)

    def get_all_capabilities(self) -> list[str]:
        return sorted(self._capability_index.keys())
