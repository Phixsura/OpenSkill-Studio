"""CDN optimizer — optimize content delivery and caching."""
from __future__ import annotations


def analyze_cdn(assets: list[dict]) -> dict:
    cached = sum(1 for a in assets if a.get("cached"))
    total_size = sum(a.get("size_kb", 0) for a in assets)
    cached_size = sum(a.get("size_kb", 0) for a in assets if a.get("cached"))
    hit_ratio = round(cached / max(len(assets), 1) * 100, 1)
    bandwidth_saved = round(cached_size / max(total_size, 1) * 100, 1)
    by_type: dict[str, int] = {}
    for a in assets:
        t = a.get("type", "other")
        by_type[t] = by_type.get(t, 0) + 1
    return {"total_assets": len(assets), "cached": cached, "uncached": len(assets) - cached,
            "hit_ratio": hit_ratio, "total_size_kb": total_size,
            "bandwidth_saved_pct": bandwidth_saved, "by_type": by_type}


def suggest_optimizations(assets: list[dict]) -> list[dict]:
    suggestions = []
    for a in assets:
        if not a.get("cached") and a.get("size_kb", 0) > 100:
            suggestions.append({"asset": a.get("path", ""), "action": "enable_caching",
                                 "reason": f"Large uncached asset ({a.get('size_kb')} KB)"})
        if a.get("type") == "image" and a.get("size_kb", 0) > 500:
            suggestions.append({"asset": a.get("path", ""), "action": "compress",
                                 "reason": f"Large image ({a.get('size_kb')} KB)"})
    return suggestions
