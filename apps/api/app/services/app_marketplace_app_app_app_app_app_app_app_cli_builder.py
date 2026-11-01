"""CLI command builder — generate CLI commands for platform operations."""
from __future__ import annotations
import html


def build_cli_command(*, command: str, args: dict | None = None,
                       flags: dict | None = None) -> dict:
    parts = [command]
    for k, v in (args or {}).items():
        parts.append(str(v))
    for k, v in (flags or {}).items():
        flag = f"--{k.replace('_', '-')}"
        if isinstance(v, bool):
            if v:
                parts.append(flag)
        else:
            parts.append(f"{flag}={v}")
    cmd_str = " ".join(parts)
    return {"command": cmd_str, "parts": parts, "copyable": cmd_str}


def generate_cli_examples(app_id: str) -> list[dict]:
    return [
        build_cli_command(command="openskill deploy", args={"app": app_id},
                           flags={"env": "production", "wait": True}),
        build_cli_command(command="openskill logs", args={"app": app_id},
                           flags={"tail": 100, "follow": True}),
        build_cli_command(command="openskill config set", args={"app": app_id},
                           flags={"key": "DEBUG", "value": "false"}),
        build_cli_command(command="openskill status", args={"app": app_id}),
    ]
