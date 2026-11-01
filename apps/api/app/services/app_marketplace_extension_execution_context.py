"""Execution Context — manage sandboxed execution contexts for extensions.

Provides isolated execution contexts with input/output binding, timeout
enforcement, resource tracking, and execution result capture.
"""
from __future__ import annotations
import secrets
import time
from dataclasses import dataclass, field
from enum import Enum


class ExecStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


@dataclass
class ExecutionContext:
    context_id: str
    extension_id: str
    function_name: str
    inputs: dict = field(default_factory=dict)
    outputs: dict = field(default_factory=dict)
    status: ExecStatus = ExecStatus.PENDING
    timeout_ms: int = 30000
    started_at: float = 0.0
    ended_at: float = 0.0
    duration_ms: float = 0.0
    error: str = ""
    memory_used_mb: float = 0.0
    cpu_time_ms: float = 0.0


class ExecutionContextService:
    """Manages sandboxed execution contexts for extension functions."""

    MAX_INPUT_SIZE = 1024 * 1024  # 1MB
    MAX_TIMEOUT = 300000  # 5 minutes

    def __init__(self):
        self._contexts: dict[str, ExecutionContext] = {}
        self._history: list[str] = []

    def create(self, extension_id: str, function_name: str,
               inputs: dict, timeout_ms: int = 30000) -> ExecutionContext:
        import json
        input_size = len(json.dumps(inputs))
        if input_size > self.MAX_INPUT_SIZE:
            raise ValueError(f"Input too large: {input_size} bytes (max {self.MAX_INPUT_SIZE})")
        if timeout_ms > self.MAX_TIMEOUT:
            raise ValueError(f"Timeout too long (max {self.MAX_TIMEOUT}ms)")
        if timeout_ms < 100:
            raise ValueError("Timeout too short (min 100ms)")

        ctx_id = f"ctx_{secrets.token_urlsafe(10)}"
        ctx = ExecutionContext(
            context_id=ctx_id, extension_id=extension_id,
            function_name=function_name, inputs=inputs,
            timeout_ms=timeout_ms,
        )
        self._contexts[ctx_id] = ctx
        self._history.append(ctx_id)
        return ctx

    def start(self, context_id: str) -> bool:
        ctx = self._contexts.get(context_id)
        if not ctx or ctx.status != ExecStatus.PENDING:
            return False
        ctx.status = ExecStatus.RUNNING
        ctx.started_at = time.time()
        return True

    def complete(self, context_id: str, outputs: dict,
                 memory_mb: float = 0, cpu_ms: float = 0) -> bool:
        ctx = self._contexts.get(context_id)
        if not ctx or ctx.status != ExecStatus.RUNNING:
            return False
        ctx.status = ExecStatus.COMPLETED
        ctx.outputs = outputs
        ctx.ended_at = time.time()
        ctx.duration_ms = round((ctx.ended_at - ctx.started_at) * 1000, 1)
        ctx.memory_used_mb = memory_mb
        ctx.cpu_time_ms = cpu_ms
        return True

    def fail(self, context_id: str, error: str) -> bool:
        ctx = self._contexts.get(context_id)
        if not ctx or ctx.status != ExecStatus.RUNNING:
            return False
        ctx.status = ExecStatus.FAILED
        ctx.error = error
        ctx.ended_at = time.time()
        ctx.duration_ms = round((ctx.ended_at - ctx.started_at) * 1000, 1)
        return True

    def timeout(self, context_id: str) -> bool:
        ctx = self._contexts.get(context_id)
        if not ctx or ctx.status != ExecStatus.RUNNING:
            return False
        ctx.status = ExecStatus.TIMEOUT
        ctx.error = f"Execution exceeded {ctx.timeout_ms}ms timeout"
        ctx.ended_at = time.time()
        ctx.duration_ms = round((ctx.ended_at - ctx.started_at) * 1000, 1)
        return True

    def cancel(self, context_id: str) -> bool:
        ctx = self._contexts.get(context_id)
        if not ctx or ctx.status not in (ExecStatus.PENDING, ExecStatus.RUNNING):
            return False
        ctx.status = ExecStatus.CANCELLED
        ctx.ended_at = time.time()
        return True

    def get(self, context_id: str) -> ExecutionContext | None:
        return self._contexts.get(context_id)

    def get_stats(self, extension_id: str) -> dict:
        ctxs = [self._contexts[cid] for cid in self._history
                if self._contexts[cid].extension_id == extension_id]
        completed = [c for c in ctxs if c.status == ExecStatus.COMPLETED]
        avg_duration = round(sum(c.duration_ms for c in completed) / len(completed), 1) if completed else 0
        return {
            "total": len(ctxs),
            "completed": len(completed),
            "failed": sum(1 for c in ctxs if c.status == ExecStatus.FAILED),
            "timeouts": sum(1 for c in ctxs if c.status == ExecStatus.TIMEOUT),
            "avg_duration_ms": avg_duration,
        }
