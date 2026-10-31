"""Fleet i18n coverage — track internationalization readiness."""
from __future__ import annotations
def fleet_i18n_coverage(strings: list[dict]) -> dict:
    translated = [s for s in strings if s.get("translated", False)]
    pct = round(len(translated) / max(len(strings), 1) * 100, 1)
    languages = len(set(s.get("lang", "en") for s in translated)) if translated else 0
    return {"total_strings": len(strings), "translated": len(translated),
            "coverage_pct": pct, "languages": languages, "ready": pct >= 90}
