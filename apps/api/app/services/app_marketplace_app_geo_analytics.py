"""Geo analytics — geographic distribution of app installations."""

from collections import defaultdict


def compute_geo_distribution(*, installs: list[dict]) -> dict:
    by_country = defaultdict(int)
    by_region = defaultdict(int)
    for inst in installs:
        country = inst.get("country", "Unknown")
        region = inst.get("region", "Unknown")
        by_country[country] += 1
        by_region[region] += 1
    countries = sorted(by_country.items(), key=lambda x: -x[1])
    regions = sorted(by_region.items(), key=lambda x: -x[1])
    return {
        "countries": [{"country": c, "count": n} for c, n in countries],
        "regions": [{"region": r, "count": n} for r, n in regions],
        "top_country": countries[0][0] if countries else None,
        "unique_countries": len(by_country),
    }


def compute_country_growth(*, current: dict[str, int], previous: dict[str, int]) -> list[dict]:
    all_countries = set(current.keys()) | set(previous.keys())
    growth = []
    for c in sorted(all_countries):
        cur = current.get(c, 0)
        prev = previous.get(c, 0)
        change = cur - prev
        growth.append({"country": c, "current": cur, "previous": prev, "change": change,
                        "growth_pct": round(change / max(prev, 1) * 100, 1)})
    return sorted(growth, key=lambda g: -g["change"])
