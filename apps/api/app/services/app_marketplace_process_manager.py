"""Process Manager — manage sandboxed extension processes.

Tracks running extension processes with PID management, timeout
enforcement, resource monitoring, and graceful shutdown.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class ProcessState(str, Enum):
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    CRASHED = "crashed"
    TIMED_OUT = "timed_out"


@dataclass
class SandboxProcess:
    process_id: str
    extension_id: str
    org_id: str
    state: ProcessState = ProcessState.STARTING
    started_at: str = ""
    stopped_at: str = ""
    timeout_seconds: int = 300
    cpu_usage: float = 0.0
    memory_mb: float = 0.0
    exit_code: int | None = None
    error: str = ""

    def __post_init__(self):
        if not self.started_at:
            self.started_at = datetime.now(timezone.utc).isoformat()


class ProcessManager:
    """Manages sandboxed extension processes."""

    def __init__(self, max_concurrent: int = 50):
        self._processes: dict[str, SandboxProcess] = {}
        self._max_concurrent = max_concurrent

    def start(self, process_id: str, extension_id: str, org_id: str,
              timeout_seconds: int = 300) -> tuple[SandboxProcess | None, str]:
        """Start a new sandboxed process."""
        running = self._count_running()
        if running >= self._max_concurrent:
            return None, f"Max concurrent processes reached ({self._max_concurrent})"

        # Check if already running for this extension+org
        for p in self._processes.values():
            if (p.extension_id == extension_id and p.org_id == org_id
                    and p.state in (ProcessState.STARTING, ProcessState.RUNNING)):
                return None, "Process already running for this extension in this org"

        proc = SandboxProcess(process_id=process_id, extension_id=extension_id,
                              org_id=org_id, state=ProcessState.RUNNING,
                              timeout_seconds=timeout_seconds)
        self._processes[process_id] = proc
        return proc, "Started"

    def stop(self, process_id: str, exit_code: int = 0) -> bool:
        proc = self._processes.get(process_id)
        if proc and proc.state == ProcessState.RUNNING:
            proc.state = ProcessState.STOPPED
            proc.exit_code = exit_code
            proc.stopped_at = datetime.now(timezone.utc).isoformat()
            return True
        return False

    def crash(self, process_id: str, error: str) -> bool:
        proc = self._processes.get(process_id)
        if proc and proc.state in (ProcessState.STARTING, ProcessState.RUNNING):
            proc.state = ProcessState.CRASHED
            proc.error = error
            proc.exit_code = 1
            proc.stopped_at = datetime.now(timezone.utc).isoformat()
            return True
        return False

    def timeout(self, process_id: str) -> bool:
        proc = self._processes.get(process_id)
        if proc and proc.state == ProcessState.RUNNING:
            proc.state = ProcessState.TIMED_OUT
            proc.error = f"Process exceeded {proc.timeout_seconds}s timeout"
            proc.stopped_at = datetime.now(timezone.utc).isoformat()
            return True
        return False

    def update_resources(self, process_id: str, cpu: float, memory_mb: float) -> bool:
        proc = self._processes.get(process_id)
        if proc and proc.state == ProcessState.RUNNING:
            proc.cpu_usage = cpu
            proc.memory_mb = memory_mb
            return True
        return False

    def get_process(self, process_id: str) -> SandboxProcess | None:
        return self._processes.get(process_id)

    def list_running(self) -> list[SandboxProcess]:
        return [p for p in self._processes.values() if p.state == ProcessState.RUNNING]

    def list_by_extension(self, extension_id: str) -> list[SandboxProcess]:
        return [p for p in self._processes.values() if p.extension_id == extension_id]

    def _count_running(self) -> int:
        return sum(1 for p in self._processes.values()
                   if p.state in (ProcessState.STARTING, ProcessState.RUNNING))
