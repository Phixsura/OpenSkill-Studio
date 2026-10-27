"""Plugin Loader — dynamic plugin loading with lifecycle and dependencies.

Implements:
- Plugin registration with metadata (name, version, deps)
- Dependency resolution order (topological sort)
- Lifecycle: load → initialize → start → stop → unload
- Plugin isolation (each has its own context)
- Hook system (plugins register hooks, host calls them)
- Conflict detection (two plugins providing same hook)
"""
from __future__ import annotations
from dataclasses import dataclass, field
from collections import deque


@dataclass
class Plugin:
    name: str
    version: str
    dependencies: list[str] = field(default_factory=list)
    hooks: dict[str, callable] = field(default_factory=dict)
    status: str = "registered"  # registered, loaded, initialized, started, stopped, error
    context: dict = field(default_factory=dict)
    error: str = ""
    init_fn: callable | None = None
    start_fn: callable | None = None
    stop_fn: callable | None = None


class PluginLoaderService:
    def __init__(self):
        self._plugins: dict[str, Plugin] = {}
        self._hook_registry: dict[str, list[tuple[str, callable]]] = {}  # hook → [(plugin, fn)]
        self._load_order: list[str] = []

    def register(self, name: str, version: str,
                 dependencies: list[str] | None = None,
                 hooks: dict[str, callable] | None = None,
                 init_fn: callable | None = None,
                 start_fn: callable | None = None,
                 stop_fn: callable | None = None) -> Plugin:
        plugin = Plugin(name=name, version=version,
                        dependencies=dependencies or [],
                        hooks=hooks or {},
                        init_fn=init_fn, start_fn=start_fn, stop_fn=stop_fn)
        self._plugins[name] = plugin
        # Register hooks
        for hook_name, hook_fn in plugin.hooks.items():
            if hook_name not in self._hook_registry:
                self._hook_registry[hook_name] = []
            self._hook_registry[hook_name].append((name, hook_fn))
        return plugin

    def resolve_order(self) -> list[str]:
        """Topological sort of plugins by dependencies."""
        in_degree = {n: 0 for n in self._plugins}
        for name, plugin in self._plugins.items():
            for dep in plugin.dependencies:
                if dep in self._plugins:
                    in_degree[name] += 1  # I depend on dep

        queue = deque(n for n, d in in_degree.items() if d == 0)
        order = []
        resolved = set()

        while queue:
            name = queue.popleft()
            order.append(name)
            resolved.add(name)
            for other, plugin in self._plugins.items():
                if name in plugin.dependencies and other not in resolved:
                    in_degree[other] -= 1
                    if in_degree[other] == 0:
                        queue.append(other)

        if len(order) != len(self._plugins):
            missing = set(self._plugins) - set(order)
            raise ValueError(f"Circular dependency or missing deps: {missing}")

        self._load_order = order
        return order

    def load_all(self) -> list[dict]:
        """Load all plugins in dependency order."""
        order = self.resolve_order()
        results = []
        for name in order:
            result = self._load_plugin(name)
            results.append(result)
        return results

    def _load_plugin(self, name: str) -> dict:
        plugin = self._plugins[name]

        # Check dependencies loaded
        for dep in plugin.dependencies:
            dep_plugin = self._plugins.get(dep)
            if not dep_plugin or dep_plugin.status not in ("loaded", "initialized", "started"):
                plugin.status = "error"
                plugin.error = f"Dependency {dep} not loaded"
                return {"plugin": name, "status": "error", "error": plugin.error}

        try:
            if plugin.init_fn:
                plugin.init_fn(plugin.context)
            plugin.status = "loaded"
            return {"plugin": name, "status": "loaded"}
        except Exception as e:
            plugin.status = "error"
            plugin.error = str(e)
            return {"plugin": name, "status": "error", "error": str(e)}

    def start(self, name: str) -> bool:
        plugin = self._plugins.get(name)
        if not plugin or plugin.status != "loaded":
            return False
        try:
            if plugin.start_fn:
                plugin.start_fn(plugin.context)
            plugin.status = "started"
            return True
        except Exception as e:
            plugin.status = "error"
            plugin.error = str(e)
            return False

    def stop(self, name: str) -> bool:
        plugin = self._plugins.get(name)
        if not plugin or plugin.status != "started":
            return False
        try:
            if plugin.stop_fn:
                plugin.stop_fn(plugin.context)
            plugin.status = "stopped"
            return True
        except Exception:
            return False

    def call_hook(self, hook_name: str, *args, **kwargs) -> list:
        """Call all plugins that registered for this hook."""
        results = []
        for plugin_name, fn in self._hook_registry.get(hook_name, []):
            plugin = self._plugins.get(plugin_name)
            if plugin and plugin.status in ("loaded", "started"):
                try:
                    results.append({"plugin": plugin_name,
                                    "result": fn(*args, **kwargs)})
                except Exception as e:
                    results.append({"plugin": plugin_name, "error": str(e)})
        return results

    def detect_conflicts(self) -> list[str]:
        """Find hooks provided by multiple plugins."""
        return [hook for hook, providers in self._hook_registry.items()
                if len(providers) > 1]

    def get_status(self) -> list[dict]:
        return [{"name": p.name, "version": p.version, "status": p.status,
                 "deps": p.dependencies, "hooks": list(p.hooks.keys())}
                for p in self._plugins.values()]
