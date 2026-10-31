"""Sandbox Process Manager — manage processes running inside extension sandboxes.

Tracks spawned processes, enforces limits, handles signals (kill/pause/resume),
monitors resource consumption per process, and prevents fork bombs.
"""
from __future__ import annotations
import secrets
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class ProcessState(str, Enum):
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    CRASHED = "crashed"
    KILLED = "killed"


@dataclass
class SandboxProcess:
    pid: str
    sandbox_id: str
    command: str
    state: ProcessState = ProcessState.RUNNING
    cpu_percent: float = 0.0
    memory_mb: float = 0.0
    started_at: str = ""
    exit_code: int | None = None

    def __post_init__(self):
        if not self.started_at:
            self.started_at = datetime.now(timezone.utc).isoformat()


class SandboxProcessService:
    """Manages processes in extension sandboxes with limits and signals."""

    MAX_PROCESSES_PER_SANDBOX = 10
    FORBIDDEN_COMMANDS = {"rm -rf /", ":(){ :|:& };:", "fork", "exec /bin/sh"}

    def __init__(self):
        self._processes: dict[str, SandboxProcess] = {}
        self._by_sandbox: dict[str, list[str]] = defaultdict(list)

    def spawn(self, sandbox_id: str, command: str) -> SandboxProcess | dict:
        # Security: block dangerous commands
        cmd_lower = command.lower().strip()
        for forbidden in self.FORBIDDEN_COMMANDS:
            if forbidden in cmd_lower:
                return {"error": f"Forbidden command pattern: {forbidden}"}

        # Enforce process limit
        active = [pid for pid in self._by_sandbox.get(sandbox_id, [])
                  if self._processes.get(pid, SandboxProcess("", "", "")).state == ProcessState.RUNNING]
        if len(active) >= self.MAX_PROCESSES_PER_SANDBOX:
            return {"error": f"Process limit ({self.MAX_PROCESSES_PER_SANDBOX}) reached"}

        pid = f"p_{secrets.token_urlsafe(8)}"
        proc = SandboxProcess(pid=pid, sandbox_id=sandbox_id, command=command)
        self._processes[pid] = proc
        self._by_sandbox[sandbox_id].append(pid)
        return proc

    def kill(self, pid: str, signal: str = "SIGTERM") -> bool:
        proc = self._processes.get(pid)
        if not proc or proc.state != ProcessState.RUNNING:
            return False
        proc.state = ProcessState.KILLED
        proc.exit_code = -9 if signal == "SIGKILL" else -15
        return True

    def pause(self, pid: str) -> bool:
        proc = self._processes.get(pid)
        if proc and proc.state == ProcessState.RUNNING:
            proc.state = ProcessState.PAUSED
            return True
        return False

    def resume(self, pid: str) -> bool:
        proc = self._processes.get(pid)
        if proc and proc.state == ProcessState.PAUSED:
            proc.state = ProcessState.RUNNING
            return True
        return False

    def crash(self, pid: str, exit_code: int = 1) -> bool:
        proc = self._processes.get(pid)
        if proc and proc.state == ProcessState.RUNNING:
            proc.state = ProcessState.CRASHED
            proc.exit_code = exit_code
            return True
        return False

    def update_metrics(self, pid: str, cpu_percent: float, memory_mb: float) -> bool:
        proc = self._processes.get(pid)
        if proc and proc.state == ProcessState.RUNNING:
            proc.cpu_percent = cpu_percent
            proc.memory_mb = memory_mb
            return True
        return False

    def kill_all(self, sandbox_id: str) -> int:
        killed = 0
        for pid in self._by_sandbox.get(sandbox_id, []):
            proc = self._processes.get(pid)
            if proc and proc.state in (ProcessState.RUNNING, ProcessState.PAUSED):
                proc.state = ProcessState.KILLED
                proc.exit_code = -9
                killed += 1
        return killed

    def list_processes(self, sandbox_id: str,
                       state: ProcessState | None = None) -> list[SandboxProcess]:
        pids = self._by_sandbox.get(sandbox_id, [])
        procs = [self._processes[p] for p in pids if p in self._processes]
        if state:
            procs = [p for p in procs if p.state == state]
        return procs

    def get_stats(self, sandbox_id: str) -> dict:
        procs = self.list_processes(sandbox_id)
        running = [p for p in procs if p.state == ProcessState.RUNNING]
        return {
            "total": len(procs),
            "running": len(running),
            "total_cpu": round(sum(p.cpu_percent for p in running), 1),
            "total_memory_mb": round(sum(p.memory_mb for p in running), 1),
        }
