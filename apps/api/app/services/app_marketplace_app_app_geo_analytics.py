"""Geo analytics — geographic distribution of app users and installs."""


COUNTRY_NAMES = {"US": "United States", "GB": "United Kingdom", "DE": "Germany",
    "FR": "France", "JP": "Japan", "IN": "India", "BR": "Brazil",
    "CA": "Canada", "AU": "Australia", "KR": "South Korea"}


def analyze_geo_distribution(*, installs: list[dict]) -> dict:
    by_country: dict[str, int] = {}
    for inst in installs:
        cc = inst.get("country", "XX")
        by_country[cc] = by_country.get(cc, 0) + 1
    total = len(installs)
    sorted_countries = sorted(by_country.items(), key=lambda x: x[1], reverse=True)
    results = [{"country_code": cc, "country_name": COUNTRY_NAMES.get(cc, cc),
                 "installs": count, "pct": round(count / max(total, 1) * 100, 1)}
                for cc, count in sorted_countries[:15]]
    top = results[0]["country_code"] if results else None
    return {"countries": results, "total_installs": total,
            "unique_countries": len(by_country), "top_country": top}
