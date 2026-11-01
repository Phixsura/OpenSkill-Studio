"""Network latency map — latency measurements between regions."""


REGIONS = {
    "us-east": {"lat": 39.0, "lng": -77.0, "label": "US East"},
    "us-west": {"lat": 37.8, "lng": -122.4, "label": "US West"},
    "eu-west": {"lat": 53.3, "lng": -6.3, "label": "Europe"},
    "ap-east": {"lat": 35.7, "lng": 139.7, "label": "Asia Pacific"},
}

LATENCY_MATRIX = {
    ("us-east", "us-west"): 65,
    ("us-east", "eu-west"): 85,
    ("us-east", "ap-east"): 170,
    ("us-west", "eu-west"): 140,
    ("us-west", "ap-east"): 110,
    ("eu-west", "ap-east"): 220,
}


def get_latency_map() -> dict:
    edges = []
    for (a, b), latency in LATENCY_MATRIX.items():
        edges.append({"from": a, "to": b, "latency_ms": latency,
                       "quality": "good" if latency < 100 else "fair" if latency < 200 else "poor"})
    return {
        "regions": [{"id": k, **v} for k, v in REGIONS.items()],
        "edges": edges,
        "total_regions": len(REGIONS),
    }


def find_optimal_region(*, user_region: str) -> dict:
    if user_region not in REGIONS:
        return {"error": f"Unknown region: {user_region}"}
    latencies = {}
    for (a, b), lat in LATENCY_MATRIX.items():
        if a == user_region:
            latencies[b] = lat
        elif b == user_region:
            latencies[a] = lat
    latencies[user_region] = 0
    nearest = min(latencies, key=latencies.get)
    return {"user_region": user_region, "optimal": nearest,
            "latency_ms": latencies[nearest], "all_latencies": latencies}
