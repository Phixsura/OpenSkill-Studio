"""Geo restriction — manage country-level app availability."""


COUNTRY_DATA = {
    "US": "United States", "GB": "United Kingdom", "DE": "Germany",
    "FR": "France", "JP": "Japan", "KR": "South Korea", "BR": "Brazil",
    "IN": "India", "AU": "Australia", "CA": "Canada", "CN": "China",
    "RU": "Russia", "SG": "Singapore", "NL": "Netherlands", "SE": "Sweden",
}


def set_geo_policy(*, app_id: str, mode: str, countries: list[str]) -> dict:
    if mode not in ("allow", "block"):
        return {"error": "Mode must be 'allow' or 'block'"}
    valid = [c for c in countries if c in COUNTRY_DATA]
    invalid = [c for c in countries if c not in COUNTRY_DATA]
    return {
        "app_id": app_id,
        "mode": mode,
        "countries": [{"code": c, "name": COUNTRY_DATA[c]} for c in valid],
        "invalid_codes": invalid,
        "coverage": f"{'Available' if mode == 'allow' else 'Blocked'} in {len(valid)} countries",
    }


def check_availability(*, country_code: str, mode: str, country_list: list[str]) -> dict:
    in_list = country_code.upper() in country_list
    available = (mode == "allow" and in_list) or (mode == "block" and not in_list)
    return {
        "country": country_code.upper(),
        "country_name": COUNTRY_DATA.get(country_code.upper(), "Unknown"),
        "available": available,
        "reason": f"Country {'in' if in_list else 'not in'} {mode} list",
    }
