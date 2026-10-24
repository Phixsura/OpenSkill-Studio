"""Fleet AI Code Generation — track AI-powered code synthesis."""
from __future__ import annotations
def fleet_ai_codegen(engines: list[dict]) -> dict:
    active = [e for e in engines if e.get("active", True)]
    completions_24h = sum(e.get("completions_24h", 0) for e in engines)
    acceptance_rate = round(sum(e.get("acceptance_pct", 0) for e in engines) / max(len(engines), 1), 1)
    languages = set()
    for e in engines:
        languages.update(e.get("languages", []))
    return {"engines": len(engines), "active": len(active), "completions_24h": completions_24h,
            "acceptance_rate": acceptance_rate, "languages": len(languages), "productive": acceptance_rate > 30}
