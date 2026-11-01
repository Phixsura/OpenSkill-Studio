"""Fleet AI SDK Generator — track automated SDK code generation."""
from __future__ import annotations
def fleet_ai_sdk_generator(generators: list[dict]) -> dict:
    active = [g for g in generators if g.get("active", True)]
    sdks_generated = sum(g.get("sdks", 0) for g in generators)
    languages = set()
    for g in generators:
        languages.update(g.get("languages", []))
    downloads_24h = sum(g.get("downloads_24h", 0) for g in generators)
    return {"generators": len(generators), "active": len(active), "sdks": sdks_generated,
            "languages": len(languages), "downloads_24h": downloads_24h, "polyglot": len(languages) > 5}
