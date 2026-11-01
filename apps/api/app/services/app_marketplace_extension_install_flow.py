"""Extension Install Flow — multi-step install with permission consent."""
from __future__ import annotations
from dataclasses import dataclass, field
import time


@dataclass
class InstallSession:
    session_id: str
    extension_id: str
    user_id: str
    step: str = "consent"  # consent, configure, install, complete, failed
    permissions_granted: list[str] = field(default_factory=list)
    config: dict = field(default_factory=dict)
    started_at: float = 0.0
    completed_at: float = 0.0
    error: str = ""
    def __post_init__(self):
        if not self.started_at: self.started_at = time.time()


class ExtInstallFlowService:
    STEPS = ["consent", "configure", "install", "complete"]

    def __init__(self):
        self._sessions: dict[str, InstallSession] = {}
        self._installed: dict[str, set[str]] = {}  # user_id -> ext_ids
        self._counter = 0

    def start(self, extension_id: str, user_id: str) -> InstallSession:
        if extension_id in self._installed.get(user_id, set()):
            raise ValueError("Already installed")
        self._counter += 1
        sid = f"inst-{self._counter}"
        s = InstallSession(session_id=sid, extension_id=extension_id, user_id=user_id)
        self._sessions[sid] = s
        return s

    def grant_permissions(self, session_id: str, permissions: list[str]) -> bool:
        s = self._sessions.get(session_id)
        if not s or s.step != "consent": return False
        s.permissions_granted = permissions
        s.step = "configure"
        return True

    def set_config(self, session_id: str, config: dict) -> bool:
        s = self._sessions.get(session_id)
        if not s or s.step != "configure": return False
        s.config = config
        s.step = "install"
        return True

    def complete(self, session_id: str) -> bool:
        s = self._sessions.get(session_id)
        if not s or s.step != "install": return False
        s.step = "complete"
        s.completed_at = time.time()
        if s.user_id not in self._installed:
            self._installed[s.user_id] = set()
        self._installed[s.user_id].add(s.extension_id)
        return True

    def fail(self, session_id: str, error: str) -> None:
        s = self._sessions.get(session_id)
        if s:
            s.step = "failed"
            s.error = error

    def is_installed(self, user_id: str, extension_id: str) -> bool:
        return extension_id in self._installed.get(user_id, set())

    def uninstall(self, user_id: str, extension_id: str) -> bool:
        exts = self._installed.get(user_id)
        if exts and extension_id in exts:
            exts.discard(extension_id)
            return True
        return False
