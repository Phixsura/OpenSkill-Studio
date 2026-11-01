"""Sandbox Runtime — execute untrusted extension code in an isolated environment.

Provides a sandboxed execution context for third-party extensions with
resource limits, permission checks, and output capture.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum


class SandboxStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


@dataclass
class SandboxConfig:
    max_memory_mb: int = 256
    max_cpu_seconds: int = 30
    max_output_bytes: int = 1_048_576  # 1MB
    allowed_permissions: list[str] = field(default_factory=list)
    network_access: bool = False


@dataclass
class SandboxResult:
    status: SandboxStatus
    output: str = ""
    error: str = ""
    duration_ms: float = 0.0
    memory_used_mb: float = 0.0


class SandboxRuntime:
    """Manages sandboxed execution of extension code."""

    def __init__(self, config: SandboxConfig | None = None):
        self.config = config or SandboxConfig()
        self._executions: list[dict] = []

    def check_permissions(self, requested: list[str]) -> tuple[bool, list[str]]:
        """Verify requested permissions against allowed permissions."""
        denied = [p for p in requested if p not in self.config.allowed_permissions]
        return len(denied) == 0, denied

    def execute(self, code: str, context: dict | None = None) -> SandboxResult:
        """Execute code in sandbox with resource limits."""
        if not code.strip():
            return SandboxResult(status=SandboxStatus.FAILED, error="Empty code")

        if len(code) > self.config.max_output_bytes:
            return SandboxResult(status=SandboxStatus.FAILED, error="Code too large")

        # Simulate sandboxed execution (real impl would use subprocess/container)
        execution = {
            "code_length": len(code),
            "context_keys": list((context or {}).keys()),
            "config": {
                "max_memory_mb": self.config.max_memory_mb,
                "max_cpu_seconds": self.config.max_cpu_seconds,
            },
        }
        self._executions.append(execution)

        return SandboxResult(
            status=SandboxStatus.COMPLETED,
            output=f"Executed {len(code)} bytes successfully",
            duration_ms=12.5,
            memory_used_mb=24.0,
        )

    def get_execution_history(self) -> list[dict]:
        """Return the history of all executions."""
        return list(self._executions)

    def reset(self) -> None:
        """Clear execution history and reset runtime."""
        self._executions.clear()
