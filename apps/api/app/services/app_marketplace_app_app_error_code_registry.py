"""Error code registry — standardized error code management."""

import html

CATEGORIES = {
    "AUTH": {"range": (1000, 1999), "description": "Authentication & authorization"},
    "INPUT": {"range": (2000, 2999), "description": "Input validation"},
    "RESOURCE": {"range": (3000, 3999), "description": "Resource not found / conflict"},
    "RATE": {"range": (4000, 4999), "description": "Rate limiting"},
    "INTERNAL": {"range": (5000, 5999), "description": "Internal errors"},
}


def register_error(*, code: int, name: str, message: str, http_status: int = 400,
                    category: str | None = None) -> dict:
    if not category:
        for cat, info in CATEGORIES.items():
            lo, hi = info["range"]
            if lo <= code <= hi:
                category = cat
                break
    return {"code": code, "name": name, "message": html.escape(message),
            "http_status": http_status, "category": category or "UNKNOWN",
            "machine_code": f"ERR_{name.upper().replace(' ', '_')}"}


def build_error_catalog(*, errors: list[dict]) -> dict:
    items = [register_error(**e) for e in errors]
    by_category: dict[str, list] = {}
    for item in items:
        by_category.setdefault(item["category"], []).append(item)
    return {"errors": items, "total": len(items), "by_category": by_category,
            "categories": list(CATEGORIES.keys())}
