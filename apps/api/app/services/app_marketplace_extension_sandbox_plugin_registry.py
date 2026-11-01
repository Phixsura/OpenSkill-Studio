"""Sandbox Plugin Registry — discover and manage sandbox plugins.

Registers plugins with metadata, version constraints, dependency
resolution, enable/disable, and plugin search.
"""
from __future__ import annotations
import secrets
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class Plugin:
    plugin_id: str
    name: str
    version: str
    description: str = ""
    author: str = ""
    tags: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    enabled: bool = True
    install_count: int = 0


class SandboxPluginRegistryService:
    """Manages sandbox plugin discovery and lifecycle."""

    def __init__(self):
        self._plugins: dict[str, dict[str, Plugin]] = defaultdict(dict)

    def register(self, sandbox_id: str, name: str, version: str,
                 description: str = "", author: str = "",
                 tags: list[str] | None = None,
                 dependencies: list[str] | None = None) -> Plugin:
        if name in self._plugins.get(sandbox_id, {}):
            raise ValueError(f"Plugin '{name}' already registered")
        plugin = Plugin(
            plugin_id=f"plg_{secrets.token_urlsafe(6)}",
            name=name, version=version, description=description,
            author=author, tags=tags or [],
            dependencies=dependencies or [],
        )
        self._plugins[sandbox_id][name] = plugin
        return plugin

    def search(self, sandbox_id: str, query: str) -> list[Plugin]:
        plugins = self._plugins.get(sandbox_id, {}).values()
        q = query.lower()
        return [p for p in plugins if q in p.name.lower()
                or q in p.description.lower()
                or any(q in t for t in p.tags)]

    def enable(self, sandbox_id: str, name: str) -> bool:
        p = self._plugins.get(sandbox_id, {}).get(name)
        if p:
            # Check dependencies are enabled
            for dep in p.dependencies:
                dep_plugin = self._plugins.get(sandbox_id, {}).get(dep)
                if not dep_plugin or not dep_plugin.enabled:
                    return False
            p.enabled = True
            return True
        return False

    def disable(self, sandbox_id: str, name: str) -> bool:
        p = self._plugins.get(sandbox_id, {}).get(name)
        if p:
            p.enabled = False
            return True
        return False

    def unregister(self, sandbox_id: str, name: str) -> bool:
        # Check no other plugin depends on this
        for other in self._plugins.get(sandbox_id, {}).values():
            if name in other.dependencies and other.enabled:
                return False  # can't remove while depended on
        return self._plugins.get(sandbox_id, {}).pop(name, None) is not None

    def check_deps(self, sandbox_id: str, name: str) -> dict:
        p = self._plugins.get(sandbox_id, {}).get(name)
        if not p:
            return {"satisfied": False, "missing": []}
        missing = [d for d in p.dependencies
                   if d not in self._plugins.get(sandbox_id, {})]
        disabled = [d for d in p.dependencies
                    if d in self._plugins.get(sandbox_id, {})
                    and not self._plugins[sandbox_id][d].enabled]
        return {"satisfied": not missing and not disabled,
                "missing": missing, "disabled": disabled}

    def list_plugins(self, sandbox_id: str, enabled_only: bool = False) -> list[Plugin]:
        plugins = list(self._plugins.get(sandbox_id, {}).values())
        if enabled_only:
            plugins = [p for p in plugins if p.enabled]
        return plugins
