"""Sandbox Debugger — interactive debugging tools for extension sandboxes.

Provides breakpoint management, variable inspection, expression evaluation,
call stack capture, and step execution for sandbox debugging.
"""
from __future__ import annotations
import secrets
from dataclasses import dataclass, field
from enum import Enum


class BreakpointType(str, Enum):
    LINE = "line"
    CONDITIONAL = "conditional"
    EXCEPTION = "exception"
    LOG = "log"


class DebugState(str, Enum):
    RUNNING = "running"
    PAUSED = "paused"
    STEPPING = "stepping"
    STOPPED = "stopped"


@dataclass
class Breakpoint:
    bp_id: str
    file: str
    line: int
    bp_type: BreakpointType = BreakpointType.LINE
    condition: str = ""
    enabled: bool = True
    hit_count: int = 0


@dataclass
class StackFrame:
    function_name: str
    file: str
    line: int
    locals: dict = field(default_factory=dict)


@dataclass
class DebugSession:
    session_id: str
    sandbox_id: str
    state: DebugState = DebugState.RUNNING
    breakpoints: list[Breakpoint] = field(default_factory=list)
    call_stack: list[StackFrame] = field(default_factory=list)
    watch_expressions: dict[str, str] = field(default_factory=dict)
    eval_history: list[dict] = field(default_factory=list)


class SandboxDebuggerService:
    """Manages debug sessions with breakpoints and inspection."""

    def __init__(self):
        self._sessions: dict[str, DebugSession] = {}

    def start_session(self, sandbox_id: str) -> DebugSession:
        session_id = f"dbg_{secrets.token_urlsafe(8)}"
        session = DebugSession(session_id=session_id, sandbox_id=sandbox_id)
        self._sessions[session_id] = session
        return session

    def add_breakpoint(self, session_id: str, file: str, line: int,
                       bp_type: BreakpointType = BreakpointType.LINE,
                       condition: str = "") -> Breakpoint | None:
        session = self._sessions.get(session_id)
        if not session:
            return None
        if line < 1:
            raise ValueError("Line number must be >= 1")
        bp = Breakpoint(
            bp_id=f"bp_{secrets.token_urlsafe(6)}",
            file=file, line=line, bp_type=bp_type, condition=condition,
        )
        session.breakpoints.append(bp)
        return bp

    def remove_breakpoint(self, session_id: str, bp_id: str) -> bool:
        session = self._sessions.get(session_id)
        if not session:
            return False
        for i, bp in enumerate(session.breakpoints):
            if bp.bp_id == bp_id:
                session.breakpoints.pop(i)
                return True
        return False

    def toggle_breakpoint(self, session_id: str, bp_id: str) -> bool:
        session = self._sessions.get(session_id)
        if not session:
            return False
        for bp in session.breakpoints:
            if bp.bp_id == bp_id:
                bp.enabled = not bp.enabled
                return True
        return False

    def hit_breakpoint(self, session_id: str, bp_id: str,
                       stack: list[dict]) -> bool:
        session = self._sessions.get(session_id)
        if not session:
            return False
        for bp in session.breakpoints:
            if bp.bp_id == bp_id and bp.enabled:
                bp.hit_count += 1
                session.state = DebugState.PAUSED
                session.call_stack = [
                    StackFrame(
                        function_name=f["function"],
                        file=f["file"], line=f["line"],
                        locals=f.get("locals", {}),
                    )
                    for f in stack
                ]
                return True
        return False

    def step(self, session_id: str, action: str = "over") -> bool:
        session = self._sessions.get(session_id)
        if not session or session.state != DebugState.PAUSED:
            return False
        session.state = DebugState.STEPPING
        return True

    def resume(self, session_id: str) -> bool:
        session = self._sessions.get(session_id)
        if not session or session.state not in (DebugState.PAUSED, DebugState.STEPPING):
            return False
        session.state = DebugState.RUNNING
        return True

    def evaluate(self, session_id: str, expression: str) -> dict:
        session = self._sessions.get(session_id)
        if not session:
            return {"error": "Session not found"}
        if session.state != DebugState.PAUSED:
            return {"error": "Can only evaluate when paused"}
        # Simulated evaluation
        result = {"expression": expression, "result": f"<eval: {expression}>",
                  "type": "string"}
        session.eval_history.append(result)
        return result

    def add_watch(self, session_id: str, name: str, expression: str) -> bool:
        session = self._sessions.get(session_id)
        if not session:
            return False
        session.watch_expressions[name] = expression
        return True

    def end_session(self, session_id: str) -> bool:
        session = self._sessions.get(session_id)
        if not session:
            return False
        session.state = DebugState.STOPPED
        return True

    def get_session(self, session_id: str) -> DebugSession | None:
        return self._sessions.get(session_id)
