"""Sandbox output parser — parse JSON-RPC responses from sandbox stdout."""

import json


def parse_sandbox_output(stdout: str) -> dict:
    """Parse sandbox stdout for JSON-RPC response."""
    lines = stdout.strip().split("\n")
    for line in reversed(lines):
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
            if isinstance(msg, dict):
                if "result" in msg:
                    return {"success": True, "output": msg["result"], "raw_line": line}
                if "error" in msg:
                    return {"success": False, "error": msg["error"].get("message", str(msg["error"])), "raw_line": line}
        except json.JSONDecodeError:
            continue
    return {"success": False, "error": "No valid JSON-RPC response found", "raw_output": stdout[:500]}


def extract_logs(stdout: str) -> list[dict]:
    """Extract non-JSON-RPC lines as log entries."""
    logs = []
    for line in stdout.strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
            if isinstance(msg, dict) and ("result" in msg or "error" in msg):
                continue  # Skip JSON-RPC responses
        except json.JSONDecodeError:
            pass
        logs.append({"level": "info", "message": line})
    return logs
