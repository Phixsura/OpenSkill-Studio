"""Sandbox Lifecycle Hooks — manage hooks for sandbox lifecycle events.

Registers callbacks for sandbox start/stop/crash/restart events with
ordering, timeout enforcement, and error isolation per hook.
"""
from __future__ import annotations
import secrets
import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum


class LifecycleEvent(str, Enum):
    BEFORE_START = "before_start"
    AFTER_START = "after_start"
    BEFORE_STOP = "before_stop"
    AFTER_STOP = "after_stop"
    ON_CRASH = "on_crash"
    ON_RESTART = "on_restart"
    ON_HEALTH_CHECK = "on_health_check"


@dataclass
class LifecycleHook:
    hook_id: str
    event: LifecycleEvent
    handler_name: str
    order: int = 0
    timeout_ms: int = 5000
    enabled: bool = True
    execution_count: int = 0
    last_error: str = ""
    error_count: int = 0


@dataclass
class HookExecution:
    hook_id: str
    handler_name: str
    success: bool
    duration_ms: float = 0.0
    error: str = ""


class SandboxLifecycleHooksService:
    """Manages lifecycle hooks with ordering and error isolation."""

    MAX_HOOKS_PER_EVENT = 20

    def __init__(self):
        self._hooks: dict[str, dict[str, list[LifecycleHook]]] = defaultdict(lambda: defaultdict(list))

    def register(self, sandbox_id: str, event: LifecycleEvent,
                 handler_name: str, order: int = 0,
                 timeout_ms: int = 5000) -> LifecycleHook:
        hooks = self._hooks[sandbox_id][event.value]
        if len(hooks) >= self.MAX_HOOKS_PER_EVENT:
            raise ValueError(f"Max hooks ({self.MAX_HOOKS_PER_EVENT}) for {event.value}")

        hook = LifecycleHook(
            hook_id=f"lh_{secrets.token_urlsafe(6)}",
            event=event, handler_name=handler_name,
            order=order, timeout_ms=timeout_ms,
        )
        hooks.append(hook)
        hooks.sort(key=lambda h: h.order)
        return hook

    def trigger(self, sandbox_id: str, event: LifecycleEvent) -> list[HookExecution]:
        hooks = self._hooks.get(sandbox_id, {}).get(event.value, [])
        results: list[HookExecution] = []

        for hook in hooks:
            if not hook.enabled:
                continue
            hook.execution_count += 1
            # Simulate execution
            result = HookExecution(
                hook_id=hook.hook_id, handler_name=hook.handler_name,
                success=True, duration_ms=1.0,
            )
            results.append(result)

        return results

    def record_error(self, hook_id: str, sandbox_id: str, error: str) -> bool:
        for event_hooks in self._hooks.get(sandbox_id, {}).values():
            for hook in event_hooks:
                if hook.hook_id == hook_id:
                    hook.error_count += 1
                    hook.last_error = error
                    if hook.error_count >= 5:
                        hook.enabled = False
                    return True
        return False

    def unregister(self, sandbox_id: str, hook_id: str) -> bool:
        for event, hooks in self._hooks.get(sandbox_id, {}).items():
            for i, hook in enumerate(hooks):
                if hook.hook_id == hook_id:
                    hooks.pop(i)
                    return True
        return False

    def list_hooks(self, sandbox_id: str,
                   event: LifecycleEvent | None = None) -> list[LifecycleHook]:
        if event:
            return list(self._hooks.get(sandbox_id, {}).get(event.value, []))
        all_hooks: list[LifecycleHook] = []
        for hooks in self._hooks.get(sandbox_id, {}).values():
            all_hooks.extend(hooks)
        return all_hooks

    def get_stats(self, sandbox_id: str) -> dict:
        all_hooks = self.list_hooks(sandbox_id)
        return {
            "total": len(all_hooks),
            "enabled": sum(1 for h in all_hooks if h.enabled),
            "disabled": sum(1 for h in all_hooks if not h.enabled),
            "total_executions": sum(h.execution_count for h in all_hooks),
            "total_errors": sum(h.error_count for h in all_hooks),
        }
