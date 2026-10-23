"""App listing preview — preview how an app will appear in the marketplace."""

import html


def generate_listing_preview(*, app: dict) -> dict:
    safe_name = html.escape(app.get("name", ""))
    safe_desc = html.escape(app.get("description", ""))
    safe_dev = html.escape(app.get("developer_name", ""))
    rating = app.get("avg_rating", 0)
    installs = app.get("install_count", 0)
    price = app.get("price", 0)
    screenshots = app.get("screenshots", [])
    return {
        "card": {
            "name": safe_name,
            "tagline": safe_desc[:80] + ("..." if len(safe_desc) > 80 else ""),
            "developer": safe_dev,
            "rating": round(rating, 1),
            "stars": "★" * round(rating) + "☆" * (5 - round(rating)),
            "install_count": f"{installs:,}",
            "price_label": "Free" if price == 0 else f"${price:.2f}/mo",
            "icon": app.get("icon_url"),
            "category": app.get("category", ""),
        },
        "detail": {
            "full_description": safe_desc,
            "screenshot_count": len(screenshots),
            "has_video": app.get("has_video", False),
            "permissions": app.get("permissions", []),
            "version": app.get("version", ""),
        },
        "completeness": _calculate_completeness(app),
    }


def _calculate_completeness(app: dict) -> dict:
    fields = {"name": bool(app.get("name")), "description": len(app.get("description", "")) >= 50,
              "icon": bool(app.get("icon_url")), "screenshots": len(app.get("screenshots", [])) >= 1,
              "category": bool(app.get("category")), "version": bool(app.get("version"))}
    done = sum(1 for v in fields.values() if v)
    return {"fields": fields, "completed": done, "total": len(fields),
            "pct": round(done / len(fields) * 100)}
