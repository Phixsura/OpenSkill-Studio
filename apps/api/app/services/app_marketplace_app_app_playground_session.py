"""Playground session — sandboxed code execution session manager."""

import secrets
import html
from datetime import datetime, timezone, timedelta


def create_session(*, language: str, user_id: str, timeout_s: int = 300) -> dict:
    session_id = f"play_{secrets.token_hex(12)}"
    now = datetime.now(timezone.utc)
    return {"session_id": session_id, "language": language, "user_id": user_id,
            "timeout_s": timeout_s, "status": "active",
            "created_at": now.isoformat(),
            "expires_at": (now + timedelta(seconds=timeout_s)).isoformat()}


def execute_code(*, session_id: str, code: str) -> dict:
    line_count = len(code.splitlines())
    char_count = len(code)
    return {"session_id": session_id, "status": "completed",
            "output": html.escape(f"Executed {line_count} lines ({char_count} chars)"),
            "line_count": line_count, "char_count": char_count,
            "execution_ms": 42, "memory_mb": 12.5}


def list_sessions(*, sessions: list[dict]) -> dict:
    active = sum(1 for s in sessions if s.get("status") == "active")
    return {"sessions": sessions, "total": len(sessions), "active": active}
