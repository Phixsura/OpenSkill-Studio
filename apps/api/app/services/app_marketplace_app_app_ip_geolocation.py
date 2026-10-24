"""IP geolocation — map IP ranges to geographic regions."""

import hashlib

# Simplified in-memory geo DB
GEO_RANGES = {
    "1.": {"country": "AU", "city": "Sydney", "lat": -33.87, "lng": 151.21},
    "8.": {"country": "US", "city": "Los Angeles", "lat": 34.05, "lng": -118.24},
    "10.": {"country": "PRIVATE", "city": "Internal", "lat": 0, "lng": 0},
    "172.": {"country": "PRIVATE", "city": "Internal", "lat": 0, "lng": 0},
    "192.": {"country": "PRIVATE", "city": "Internal", "lat": 0, "lng": 0},
}


def lookup_ip(*, ip: str) -> dict:
    prefix = ip.split(".")[0] + "."
    geo = GEO_RANGES.get(prefix, {"country": "US", "city": "Unknown", "lat": 37.77, "lng": -122.42})
    return {"ip": ip, "country": geo["country"], "city": geo["city"],
            "latitude": geo["lat"], "longitude": geo["lng"],
            "is_private": geo["country"] == "PRIVATE"}


def build_geo_distribution(*, ips: list[str]) -> dict:
    by_country: dict[str, int] = {}
    for ip in ips:
        r = lookup_ip(ip=ip)
        if not r["is_private"]:
            by_country[r["country"]] = by_country.get(r["country"], 0) + 1
    top = sorted(by_country.items(), key=lambda x: -x[1])
    return {"distribution": [{"country": c, "count": n} for c, n in top],
            "total_ips": len(ips), "countries": len(by_country)}
