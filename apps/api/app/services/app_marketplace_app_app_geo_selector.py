"""Geo selector — region selection for multi-region deployments."""

import html

REGIONS = {
    "us-east-1": {"name": "US East (Virginia)", "flag": "🇺🇸", "continent": "North America", "latency_ms": 20},
    "us-west-2": {"name": "US West (Oregon)", "flag": "🇺🇸", "continent": "North America", "latency_ms": 45},
    "eu-west-1": {"name": "EU West (Ireland)", "flag": "🇮🇪", "continent": "Europe", "latency_ms": 80},
    "eu-central-1": {"name": "EU Central (Frankfurt)", "flag": "🇩🇪", "continent": "Europe", "latency_ms": 85},
    "ap-northeast-1": {"name": "Asia Pacific (Tokyo)", "flag": "🇯🇵", "continent": "Asia Pacific", "latency_ms": 120},
    "ap-southeast-1": {"name": "Asia Pacific (Singapore)", "flag": "🇸🇬", "continent": "Asia Pacific", "latency_ms": 130},
}


def list_regions(*, continent: str | None = None) -> dict:
    items = []
    for rid, r in REGIONS.items():
        if continent and r["continent"] != continent:
            continue
        items.append({"id": rid, "name": r["name"], "flag": r["flag"],
                       "continent": r["continent"], "latency_ms": r["latency_ms"]})
    items.sort(key=lambda x: x["latency_ms"])
    continents = sorted(set(r["continent"] for r in REGIONS.values()))
    return {"regions": items, "total": len(items), "continents": continents}


def recommend_region(*, user_continent: str) -> dict:
    matches = [r for r in REGIONS.items() if r[1]["continent"] == user_continent]
    if not matches:
        matches = list(REGIONS.items())
    best = min(matches, key=lambda x: x[1]["latency_ms"])
    return {"recommended": best[0], "name": best[1]["name"], "flag": best[1]["flag"],
            "latency_ms": best[1]["latency_ms"]}
