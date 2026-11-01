"""Playground snippet runner — execute code snippets safely."""
from __future__ import annotations
import time
import hashlib


def create_snippet(language: str, code: str, author: str = "") -> dict:
    snippet_id = hashlib.sha256(f"{code}:{time.time()}".encode()).hexdigest()[:10]
    lines = code.strip().count("\n") + 1
    return {"id": snippet_id, "language": language, "code": code,
            "author": author, "lines": lines, "created_at": time.time()}


def simulate_run(snippet: dict, timeout_ms: int = 5000) -> dict:
    lang = snippet["language"]
    supported = {"python", "javascript", "typescript", "shell", "ruby"}
    if lang not in supported:
        return {"success": False, "error": f"unsupported language: {lang}"}
    duration = min(len(snippet["code"]) * 0.1, timeout_ms)
    return {"success": True, "snippet_id": snippet["id"], "language": lang,
            "duration_ms": round(duration, 1), "output": f"[simulated {lang} output]",
            "exit_code": 0}


def snippet_stats(snippets: list[dict]) -> dict:
    by_lang: dict[str, int] = {}
    total_lines = 0
    for s in snippets:
        by_lang[s["language"]] = by_lang.get(s["language"], 0) + 1
        total_lines += s["lines"]
    return {"total": len(snippets), "by_language": by_lang,
            "total_lines": total_lines, "languages": sorted(by_lang.keys())}
