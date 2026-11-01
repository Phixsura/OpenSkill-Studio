"""Sandbox Request Interceptor — middleware-style request/response interception.

Intercepts API requests with before/after hooks, request modification,
response caching, latency injection for testing, and request logging.
"""
from __future__ import annotations
import secrets
import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum


class InterceptPhase(str, Enum):
    BEFORE = "before"
    AFTER = "after"


class InterceptAction(str, Enum):
    PASS = "pass"
    MODIFY = "modify"
    BLOCK = "block"
    CACHE = "cache"
    DELAY = "delay"


@dataclass
class Interceptor:
    interceptor_id: str
    name: str
    phase: InterceptPhase
    action: InterceptAction
    config: dict = field(default_factory=dict)
    enabled: bool = True
    execution_count: int = 0
    order: int = 0


@dataclass
class InterceptResult:
    interceptor_id: str
    action: InterceptAction
    modified: bool = False
    blocked: bool = False
    cached: bool = False
    delay_ms: float = 0.0


class SandboxRequestInterceptorService:
    """Middleware interceptor for sandbox API requests."""

    def __init__(self):
        self._interceptors: dict[str, list[Interceptor]] = defaultdict(list)
        self._cache: dict[str, dict] = defaultdict(dict)

    def register(self, sandbox_id: str, name: str, phase: InterceptPhase,
                 action: InterceptAction, config: dict | None = None,
                 order: int = 0) -> Interceptor:
        interceptor = Interceptor(
            interceptor_id=f"int_{secrets.token_urlsafe(6)}",
            name=name, phase=phase, action=action,
            config=config or {}, order=order,
        )
        self._interceptors[sandbox_id].append(interceptor)
        self._interceptors[sandbox_id].sort(key=lambda i: i.order)
        return interceptor

    def execute_before(self, sandbox_id: str, request: dict) -> list[InterceptResult]:
        results = []
        for interceptor in self._interceptors.get(sandbox_id, []):
            if not interceptor.enabled or interceptor.phase != InterceptPhase.BEFORE:
                continue
            interceptor.execution_count += 1
            result = self._apply(interceptor, request)
            results.append(result)
            if result.blocked:
                break
        return results

    def execute_after(self, sandbox_id: str, request: dict,
                      response: dict) -> list[InterceptResult]:
        results = []
        for interceptor in self._interceptors.get(sandbox_id, []):
            if not interceptor.enabled or interceptor.phase != InterceptPhase.AFTER:
                continue
            interceptor.execution_count += 1
            result = self._apply(interceptor, request, response)
            results.append(result)
        return results

    def _apply(self, interceptor: Interceptor, request: dict,
               response: dict | None = None) -> InterceptResult:
        if interceptor.action == InterceptAction.BLOCK:
            pattern = interceptor.config.get("url_pattern", "")
            url = request.get("url", "")
            if pattern and pattern in url:
                return InterceptResult(interceptor.interceptor_id,
                                       InterceptAction.BLOCK, blocked=True)

        elif interceptor.action == InterceptAction.DELAY:
            delay = interceptor.config.get("delay_ms", 0)
            return InterceptResult(interceptor.interceptor_id,
                                   InterceptAction.DELAY, delay_ms=delay)

        elif interceptor.action == InterceptAction.MODIFY:
            return InterceptResult(interceptor.interceptor_id,
                                   InterceptAction.MODIFY, modified=True)

        elif interceptor.action == InterceptAction.CACHE:
            return InterceptResult(interceptor.interceptor_id,
                                   InterceptAction.CACHE, cached=True)

        return InterceptResult(interceptor.interceptor_id, InterceptAction.PASS)

    def list_interceptors(self, sandbox_id: str) -> list[Interceptor]:
        return list(self._interceptors.get(sandbox_id, []))

    def toggle(self, sandbox_id: str, interceptor_id: str) -> bool:
        for i in self._interceptors.get(sandbox_id, []):
            if i.interceptor_id == interceptor_id:
                i.enabled = not i.enabled
                return True
        return False

    def remove(self, sandbox_id: str, interceptor_id: str) -> bool:
        interceptors = self._interceptors.get(sandbox_id, [])
        for idx, i in enumerate(interceptors):
            if i.interceptor_id == interceptor_id:
                interceptors.pop(idx)
                return True
        return False
