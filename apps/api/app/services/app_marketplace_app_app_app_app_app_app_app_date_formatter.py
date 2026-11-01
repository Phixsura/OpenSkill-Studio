"""Date formatter — relative and absolute date formatting for the platform."""
from __future__ import annotations


def format_relative(seconds_ago: float) -> str:
    if seconds_ago < 60:
        return "just now"
    if seconds_ago < 3600:
        m = int(seconds_ago / 60)
        return f"{m}m ago"
    if seconds_ago < 86400:
        h = int(seconds_ago / 3600)
        return f"{h}h ago"
    if seconds_ago < 604800:
        d = int(seconds_ago / 86400)
        return f"{d}d ago"
    if seconds_ago < 2592000:
        w = int(seconds_ago / 604800)
        return f"{w}w ago"
    if seconds_ago < 31536000:
        mo = int(seconds_ago / 2592000)
        return f"{mo}mo ago"
    y = int(seconds_ago / 31536000)
    return f"{y}y ago"


def format_duration(seconds: float) -> str:
    if seconds < 1:
        return f"{int(seconds * 1000)}ms"
    if seconds < 60:
        return f"{seconds:.1f}s"
    if seconds < 3600:
        m = int(seconds / 60)
        s = int(seconds % 60)
        return f"{m}m {s}s"
    h = int(seconds / 3600)
    m = int((seconds % 3600) / 60)
    return f"{h}h {m}m"


def format_number(n: int | float) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(int(n))
