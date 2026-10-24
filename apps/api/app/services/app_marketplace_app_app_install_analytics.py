"""App install analytics — analyze installation patterns and sources."""


def analyze_installs(*, installs: list[dict]) -> dict:
    total = len(installs)
    by_source: dict[str, int] = {}
    by_platform: dict[str, int] = {}
    by_day: dict[str, int] = {}
    for inst in installs:
        src = inst.get("source", "direct")
        by_source[src] = by_source.get(src, 0) + 1
        plat = inst.get("platform", "web")
        by_platform[plat] = by_platform.get(plat, 0) + 1
        day = inst.get("date", "")[:10]
        if day:
            by_day[day] = by_day.get(day, 0) + 1
    top_source = max(by_source, key=by_source.get) if by_source else None
    return {
        "total_installs": total,
        "by_source": dict(sorted(by_source.items(), key=lambda x: x[1], reverse=True)),
        "by_platform": by_platform,
        "daily": dict(sorted(by_day.items())),
        "top_source": top_source,
        "unique_days": len(by_day),
    }
