"""Plugin Hooks — lifecycle hook system for extension plugins.

Registers and executes hooks at defined lifecycle points (install, activate,
deactivate, update, uninstall) with priority ordering and error isolation.
"""
from __future__ import annotations
import secrets
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum


class HookPoint(str, Enum):
    PRE_INSTALL = "pre_install"
    POST_INSTALL = "post_install"
    PRE_ACTIVATE = "pre_activate"
    POST_ACTIVATE = "post_activate"
    PRE_DEACTIVATE = "pre_deactivate"
    POST_DEACTIVATE = "post_deactivate"
    PRE_UPDATE = "pre_update"
    POST_UPDATE = "post_update"
    PRE_UNINSTALL = "pre_uninstall"
    POST_UNINSTALL = "post_uninstall"
    ON_ERROR = "on_error"
    ON_CONFIG_CHANGE = "on_config_change"


@dataclass
class HookRegistration:
    hook_id: str
    extension_id: str
    hook_point: HookPoint
    handler_name: str
    priority: int = 0  # higher = runs first
    enabled: bool = True
    timeout_ms: int = 5000
    error_count: int = 0
    max_errors: int = 5


@dataclass
class HookResult:
    hook_id: str
    handler_name: str
    success: bool
    result: str = ""
    error: str = ""
    duration_ms: float = 0.0


class PluginHooksService:
    """Manages extension lifecycle hooks with priority and error isolation."""

    def __init__(self):
        self._hooks: dict[str, HookRegistration] = {}
        self._by_point: dict[str, dict[HookPoint, list[str]]] = defaultdict(lambda: defaultdict(list))
        self._execution_log: list[dict] = []

    def register(self, extension_id: str, hook_point: HookPoint,
                 handler_name: str, priority: int = 0,
                 timeout_ms: int = 5000) -> HookRegistration:
        hook_id = f"hk_{secrets.token_urlsafe(8)}"
        hook = HookRegistration(
            hook_id=hook_id, extension_id=extension_id,
            hook_point=hook_point, handler_name=handler_name,
            priority=priority, timeout_ms=timeout_ms,
        )
        self._hooks[hook_id] = hook
        self._by_point[extension_id][hook_point].append(hook_id)
        return hook

    def execute(self, extension_id: str, hook_point: HookPoint,
                context: dict | None = None) -> list[HookResult]:
        hook_ids = self._by_point.get(extension_id, {}).get(hook_point, [])
        hooks = [self._hooks[hid] for hid in hook_ids
                 if self._hooks[hid].enabled]
        # Sort by priority (higher first)
        hooks.sort(key=lambda h: h.priority, reverse=True)

        results: list[HookResult] = []
        for hook in hooks:
            # Simulate execution — in production this would call the handler
            result = HookResult(
                hook_id=hook.hook_id,
                handler_name=hook.handler_name,
                success=True,
                result=f"Executed {hook.handler_name}",
            )
            results.append(result)
            self._execution_log.append({
                "extension_id": extension_id, "hook_point": hook_point.value,
                "handler": hook.handler_name, "success": True,
            })

        return results

    def record_error(self, hook_id: str, error: str) -> bool:
        hook = self._hooks.get(hook_id)
        if not hook:
            return False
        hook.error_count += 1
        if hook.error_count >= hook.max_errors:
            hook.enabled = False
        self._execution_log.append({
            "hook_id": hook_id, "error": error,
            "disabled": not hook.enabled,
        })
        return True

    def disable(self, hook_id: str) -> bool:
        hook = self._hooks.get(hook_id)
        if hook:
            hook.enabled = False
            return True
        return False

    def enable(self, hook_id: str) -> bool:
        hook = self._hooks.get(hook_id)
        if hook:
            hook.enabled = True
            hook.error_count = 0
            return True
        return False

    def list_hooks(self, extension_id: str,
                   hook_point: HookPoint | None = None) -> list[HookRegistration]:
        all_hooks = [h for h in self._hooks.values() if h.extension_id == extension_id]
        if hook_point:
            all_hooks = [h for h in all_hooks if h.hook_point == hook_point]
        return sorted(all_hooks, key=lambda h: h.priority, reverse=True)

    def unregister(self, hook_id: str) -> bool:
        hook = self._hooks.pop(hook_id, None)
        if hook:
            ids = self._by_point.get(hook.extension_id, {}).get(hook.hook_point, [])
            if hook_id in ids:
                ids.remove(hook_id)
            return True
        return False
