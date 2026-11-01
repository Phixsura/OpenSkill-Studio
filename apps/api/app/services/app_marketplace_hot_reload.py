"""Hot Reload Manager — manage live reloading of extensions during development.

Tracks file changes, triggers rebuild/restart cycles, and maintains
WebSocket connections for instant feedback during development.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class ReloadStatus(str, Enum):
    IDLE = "idle"
    WATCHING = "watching"
    REBUILDING = "rebuilding"
    RELOADING = "reloading"
    ERROR = "error"


@dataclass
class FileChange:
    path: str
    change_type: str  # "created", "modified", "deleted"
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


@dataclass
class ReloadSession:
    session_id: str
    extension_id: str
    status: ReloadStatus = ReloadStatus.IDLE
    watch_paths: list[str] = field(default_factory=list)
    ignore_patterns: list[str] = field(default_factory=lambda: ["*.pyc", "__pycache__", ".git", "node_modules"])
    reload_count: int = 0
    last_reload_at: str = ""
    errors: list[str] = field(default_factory=list)


class HotReloadManager:
    """Manages hot reload sessions for extension development."""

    def __init__(self, debounce_ms: int = 300):
        self._sessions: dict[str, ReloadSession] = {}
        self._change_queue: dict[str, list[FileChange]] = {}
        self._debounce_ms = debounce_ms

    def start_session(self, session_id: str, extension_id: str,
                      watch_paths: list[str]) -> ReloadSession:
        session = ReloadSession(
            session_id=session_id, extension_id=extension_id,
            status=ReloadStatus.WATCHING, watch_paths=watch_paths,
        )
        self._sessions[session_id] = session
        self._change_queue[session_id] = []
        return session

    def stop_session(self, session_id: str) -> bool:
        session = self._sessions.get(session_id)
        if session:
            session.status = ReloadStatus.IDLE
            return True
        return False

    def should_ignore(self, session_id: str, path: str) -> bool:
        """Check if a file change should be ignored."""
        session = self._sessions.get(session_id)
        if not session:
            return True
        for pattern in session.ignore_patterns:
            clean = pattern.replace("*", "")
            if clean in path:
                return True
        return False

    def record_change(self, session_id: str, change: FileChange) -> bool:
        """Record a file change event."""
        if self.should_ignore(session_id, change.path):
            return False
        self._change_queue.setdefault(session_id, []).append(change)
        return True

    def trigger_reload(self, session_id: str) -> dict | None:
        """Trigger a reload cycle for pending changes."""
        session = self._sessions.get(session_id)
        if not session or session.status not in (ReloadStatus.WATCHING, ReloadStatus.ERROR):
            return None

        changes = self._change_queue.get(session_id, [])
        if not changes:
            return None

        session.status = ReloadStatus.REBUILDING
        session.reload_count += 1
        session.last_reload_at = datetime.now(timezone.utc).isoformat()

        result = {
            "session_id": session_id,
            "reload_number": session.reload_count,
            "changes_processed": len(changes),
            "files_changed": [c.path for c in changes],
            "status": "success",
        }

        self._change_queue[session_id] = []
        session.status = ReloadStatus.WATCHING
        return result

    def get_session(self, session_id: str) -> ReloadSession | None:
        return self._sessions.get(session_id)

    def get_pending_changes(self, session_id: str) -> list[FileChange]:
        return list(self._change_queue.get(session_id, []))

    def list_active_sessions(self) -> list[ReloadSession]:
        return [s for s in self._sessions.values() if s.status != ReloadStatus.IDLE]
