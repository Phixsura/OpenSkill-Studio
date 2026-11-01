"""Sandbox runtime — isolated app execution environment config."""

import secrets
import html
from datetime import datetime, timezone


def create_sandbox(*, app_id: str, runtime: str = "node18",
                    memory_mb: int = 256, timeout_s: int = 30) -> dict:
    sandbox_id = f"sbx_{secrets.token_hex(8)}"
    return {"sandbox_id": sandbox_id, "app_id": app_id, "runtime": runtime,
            "memory_mb": memory_mb, "timeout_s": timeout_s, "status": "creating",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "env_vars": {}, "network_enabled": False, "fs_readonly": True}


RUNTIMES = {
    "node18": {"label": "Node.js 18", "icon": "🟢", "extensions": [".js", ".ts"]},
    "node20": {"label": "Node.js 20", "icon": "🟢", "extensions": [".js", ".ts"]},
    "python311": {"label": "Python 3.11", "icon": "🐍", "extensions": [".py"]},
    "python312": {"label": "Python 3.12", "icon": "🐍", "extensions": [".py"]},
    "deno": {"label": "Deno", "icon": "🦕", "extensions": [".ts", ".js"]},
    "bun": {"label": "Bun", "icon": "🍞", "extensions": [".ts", ".js"]},
}


def list_runtimes() -> list[dict]:
    return [{"id": k, **v} for k, v in RUNTIMES.items()]
