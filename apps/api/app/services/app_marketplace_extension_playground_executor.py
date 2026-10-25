"""Playground Executor — execute code snippets in a sandboxed playground.

Provides a safe execution environment for developers to test extension
code snippets with mock platform APIs, capturing stdout and errors.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class ExecutionResult:
    snippet_id: str
    stdout: str
    stderr: str
    return_value: object | None
    duration_ms: float
    success: bool
    error_type: str = ""
    memory_used_mb: float = 0.0
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


class PlaygroundExecutor:
    """Executes code snippets in a sandboxed playground."""

    def __init__(self, timeout_ms: float = 5000, memory_limit_mb: float = 128):
        self._timeout = timeout_ms
        self._memory_limit = memory_limit_mb
        self._history: dict[str, list[ExecutionResult]] = {}
        self._counter = 0

    def execute(self, extension_id: str, code: str, context: dict | None = None) -> ExecutionResult:
        """Execute a code snippet (simulated safe execution)."""
        self._counter += 1
        snippet_id = f"snip-{self._counter}"

        # Basic validation
        if not code.strip():
            return ExecutionResult(snippet_id, "", "Empty code", None, 0, False, "EmptyCode")

        if len(code) > 100000:
            return ExecutionResult(snippet_id, "", "Code too large", None, 0, False, "SizeLimit")

        # Simulated execution
        stdout_lines = []
        return_value = None
        error = ""
        success = True

        try:
            # Simulate: count print statements and assignments
            lines = code.strip().split("\n")
            for line in lines:
                stripped = line.strip()
                if stripped.startswith("print("):
                    content = stripped[6:-1].strip("'\"")
                    stdout_lines.append(content)
                elif "=" in stripped and not stripped.startswith("#"):
                    parts = stripped.split("=", 1)
                    return_value = parts[1].strip().strip("'\"")
            duration = len(lines) * 2.5  # simulated timing
        except Exception as e:
            error = str(e)
            success = False
            duration = 0

        result = ExecutionResult(
            snippet_id=snippet_id,
            stdout="\n".join(stdout_lines),
            stderr=error,
            return_value=return_value,
            duration_ms=duration,
            success=success,
            error_type="" if success else "RuntimeError",
            memory_used_mb=len(code) / 1024,
        )
        self._history.setdefault(extension_id, []).append(result)
        return result

    def get_history(self, extension_id: str, limit: int = 20) -> list[ExecutionResult]:
        return self._history.get(extension_id, [])[-limit:]

    def clear_history(self, extension_id: str) -> int:
        count = len(self._history.get(extension_id, []))
        self._history.pop(extension_id, None)
        return count

    def get_stats(self, extension_id: str) -> dict:
        history = self._history.get(extension_id, [])
        if not history:
            return {"executions": 0, "success_rate": 0, "avg_duration_ms": 0}
        successes = sum(1 for r in history if r.success)
        return {
            "executions": len(history),
            "success_rate": round(successes / len(history) * 100, 1),
            "avg_duration_ms": round(sum(r.duration_ms for r in history) / len(history), 2),
        }
