"""Sandbox REPL — interactive Read-Eval-Print-Loop for extension sandboxes.

Executes code snippets in sandbox context with output capture,
error handling, command history, and context-aware autocomplete hints.
"""
from __future__ import annotations
import secrets
import time
from dataclasses import dataclass, field


@dataclass
class ReplResult:
    input_code: str
    output: str
    error: str = ""
    execution_time_ms: float = 0.0
    result_type: str = "string"


@dataclass
class ReplSession:
    session_id: str
    sandbox_id: str
    runtime: str
    history: list[ReplResult] = field(default_factory=list)
    context: dict = field(default_factory=dict)  # persistent variables
    max_history: int = 100


DANGEROUS_PATTERNS = [
    "import os", "import sys", "import subprocess", "import shutil",
    "__import__", "eval(", "exec(", "open(", "compile(",
    "require('child_process')", "require('fs')", "Deno.run",
]


class SandboxReplService:
    """Manages REPL sessions for extension sandbox debugging."""

    MAX_CODE_LENGTH = 10000
    MAX_EXECUTION_TIME_MS = 5000

    def __init__(self):
        self._sessions: dict[str, ReplSession] = {}

    def create_session(self, sandbox_id: str, runtime: str = "node20") -> ReplSession:
        session_id = f"repl_{secrets.token_urlsafe(8)}"
        session = ReplSession(
            session_id=session_id, sandbox_id=sandbox_id, runtime=runtime,
        )
        self._sessions[session_id] = session
        return session

    def execute(self, session_id: str, code: str) -> ReplResult:
        session = self._sessions.get(session_id)
        if not session:
            return ReplResult(input_code=code, output="", error="Session not found")

        if len(code) > self.MAX_CODE_LENGTH:
            return ReplResult(input_code=code[:50] + "...", output="",
                              error=f"Code too long (max {self.MAX_CODE_LENGTH} chars)")

        if not code.strip():
            return ReplResult(input_code=code, output="", error="Empty input")

        # Security check
        for pattern in DANGEROUS_PATTERNS:
            if pattern in code:
                return ReplResult(input_code=code, output="",
                                  error=f"Blocked: {pattern} is not allowed in sandbox")

        # Simulated execution
        start = time.time()
        try:
            output, result_type = self._simulate_exec(code, session)
            elapsed = round((time.time() - start) * 1000, 2)
            result = ReplResult(
                input_code=code, output=output,
                execution_time_ms=elapsed, result_type=result_type,
            )
        except Exception as e:
            result = ReplResult(
                input_code=code, output="", error=str(e),
                execution_time_ms=round((time.time() - start) * 1000, 2),
            )

        session.history.append(result)
        if len(session.history) > session.max_history:
            session.history = session.history[-session.max_history:]

        return result

    def _simulate_exec(self, code: str, session: ReplSession) -> tuple[str, str]:
        # Simple expression evaluation for demo
        if code.startswith("let ") or code.startswith("const ") or "=" in code.split("(")[0]:
            parts = code.split("=", 1)
            if len(parts) == 2:
                var_name = parts[0].replace("let ", "").replace("const ", "").replace("var ", "").strip()
                session.context[var_name] = parts[1].strip()
                return f"{var_name} = {parts[1].strip()}", "assignment"
        if code in session.context:
            return session.context[code], "variable"
        return f"=> {code}", "expression"

    def get_history(self, session_id: str, limit: int = 20) -> list[ReplResult]:
        session = self._sessions.get(session_id)
        if not session:
            return []
        return session.history[-limit:]

    def clear_context(self, session_id: str) -> bool:
        session = self._sessions.get(session_id)
        if session:
            session.context.clear()
            return True
        return False

    def get_completions(self, session_id: str, prefix: str) -> list[str]:
        session = self._sessions.get(session_id)
        if not session:
            return []
        matches = [k for k in session.context if k.startswith(prefix)]
        builtins = ["console.log", "JSON.stringify", "JSON.parse",
                     "Array.from", "Object.keys", "Math."]
        matches.extend(b for b in builtins if b.startswith(prefix))
        return sorted(set(matches))[:10]

    def end_session(self, session_id: str) -> bool:
        return self._sessions.pop(session_id, None) is not None
