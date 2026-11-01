"""Sandbox Performance Profiler — profile extension execution performance.

Captures function-level execution time, memory allocation, call counts,
hotspot detection, and flamegraph-ready stack traces.
"""
from __future__ import annotations
import secrets
import time
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class ProfileEntry:
    function_name: str
    file: str
    line: int = 0
    total_time_ms: float = 0.0
    self_time_ms: float = 0.0
    call_count: int = 0
    avg_time_ms: float = 0.0
    memory_delta_kb: float = 0.0


@dataclass
class ProfileSession:
    session_id: str
    sandbox_id: str
    status: str = "idle"  # idle, profiling, completed
    entries: list[ProfileEntry] = field(default_factory=list)
    total_time_ms: float = 0.0
    started_at: float = 0.0
    ended_at: float = 0.0


class SandboxPerformanceProfilerService:
    """Profiles extension code execution with hotspot detection."""

    def __init__(self):
        self._sessions: dict[str, ProfileSession] = {}

    def start_session(self, sandbox_id: str) -> ProfileSession:
        session_id = f"prof_{secrets.token_urlsafe(8)}"
        session = ProfileSession(
            session_id=session_id, sandbox_id=sandbox_id,
            status="profiling", started_at=time.time(),
        )
        self._sessions[session_id] = session
        return session

    def record(self, session_id: str, function_name: str, file: str,
               line: int = 0, time_ms: float = 0, self_time_ms: float = 0,
               memory_delta_kb: float = 0) -> bool:
        session = self._sessions.get(session_id)
        if not session or session.status != "profiling":
            return False

        # Find or create entry
        existing = next((e for e in session.entries
                         if e.function_name == function_name and e.file == file), None)
        if existing:
            existing.call_count += 1
            existing.total_time_ms += time_ms
            existing.self_time_ms += self_time_ms
            existing.memory_delta_kb += memory_delta_kb
            existing.avg_time_ms = round(existing.total_time_ms / existing.call_count, 2)
        else:
            session.entries.append(ProfileEntry(
                function_name=function_name, file=file, line=line,
                total_time_ms=time_ms, self_time_ms=self_time_ms,
                call_count=1, avg_time_ms=round(time_ms, 2),
                memory_delta_kb=memory_delta_kb,
            ))
        return True

    def stop_session(self, session_id: str) -> ProfileSession | None:
        session = self._sessions.get(session_id)
        if not session or session.status != "profiling":
            return None
        session.status = "completed"
        session.ended_at = time.time()
        session.total_time_ms = round((session.ended_at - session.started_at) * 1000, 1)
        return session

    def get_hotspots(self, session_id: str, limit: int = 10) -> list[ProfileEntry]:
        session = self._sessions.get(session_id)
        if not session:
            return []
        return sorted(session.entries, key=lambda e: e.self_time_ms, reverse=True)[:limit]

    def get_by_calls(self, session_id: str, limit: int = 10) -> list[ProfileEntry]:
        session = self._sessions.get(session_id)
        if not session:
            return []
        return sorted(session.entries, key=lambda e: e.call_count, reverse=True)[:limit]

    def get_memory_hotspots(self, session_id: str, limit: int = 10) -> list[ProfileEntry]:
        session = self._sessions.get(session_id)
        if not session:
            return []
        return sorted(session.entries, key=lambda e: e.memory_delta_kb, reverse=True)[:limit]

    def get_summary(self, session_id: str) -> dict:
        session = self._sessions.get(session_id)
        if not session:
            return {}
        return {
            "status": session.status,
            "total_time_ms": session.total_time_ms,
            "total_functions": len(session.entries),
            "total_calls": sum(e.call_count for e in session.entries),
            "total_memory_kb": round(sum(e.memory_delta_kb for e in session.entries), 1),
        }
