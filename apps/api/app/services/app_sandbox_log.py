"""Sandbox log parser — parse and filter sandbox execution logs."""

import json
import re
from datetime import datetime, UTC

LEVEL_ORDER = {"debug": 0, "info": 1, "warn": 2, "error": 3, "fatal": 4}
ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def parse_log_line(line: str) -> dict | None:
    """Parse a single log line from sandbox stdout/stderr.
    
    Supports JSON format and plain text with level prefix.
    """
    line = line.strip()
    if not line:
        return None

    # Try JSON format
    try:
        parsed = json.loads(line)
        if isinstance(parsed, dict) and "message" in parsed:
            return {
                "level": parsed.get("level", "info"),
                "message": parsed["message"],
                "timestamp": parsed.get("timestamp", datetime.now(UTC).isoformat()),
                "extra": {k: v for k, v in parsed.items() if k not in ("level", "message", "timestamp")},
            }
    except (json.JSONDecodeError, TypeError):
        pass

    # Strip ANSI codes
    clean = ANSI_RE.sub("", line)

    # Try level prefix: [INFO] message or INFO: message
    for level in LEVEL_ORDER:
        prefix_bracket = f"[{level.upper()}]"
        prefix_colon = f"{level.upper()}:"
        if clean.upper().startswith(prefix_bracket):
            return {"level": level, "message": clean[len(prefix_bracket):].strip(),
                    "timestamp": datetime.now(UTC).isoformat(), "extra": {}}
        if clean.upper().startswith(prefix_colon):
            return {"level": level, "message": clean[len(prefix_colon):].strip(),
                    "timestamp": datetime.now(UTC).isoformat(), "extra": {}}

    # Default: info level
    return {"level": "info", "message": clean, "timestamp": datetime.now(UTC).isoformat(), "extra": {}}


def parse_logs(output: str) -> list[dict]:
    """Parse multi-line sandbox output into structured logs."""
    return [entry for line in output.split("\n") if (entry := parse_log_line(line)) is not None]


def filter_logs(logs: list[dict], *, min_level: str = "debug") -> list[dict]:
    """Filter logs by minimum severity level."""
    min_order = LEVEL_ORDER.get(min_level, 0)
    return [log for log in logs if LEVEL_ORDER.get(log.get("level", "info"), 1) >= min_order]
