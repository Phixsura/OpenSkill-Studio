"""Platform stats — aggregate marketplace statistics."""


def build_platform_stats(*, apps: int, developers: int, downloads: int,
                           reviews: int, api_calls: int) -> dict:
    def compact(n: int) -> str:
        if n >= 1_000_000:
            return f"{n/1_000_000:.1f}M"
        if n >= 1_000:
            return f"{n/1_000:.1f}K"
        return str(n)

    return {
        "stats": [
            {"label": "Apps", "value": apps, "display": compact(apps), "icon": "📦"},
            {"label": "Developers", "value": developers, "display": compact(developers), "icon": "👩‍💻"},
            {"label": "Downloads", "value": downloads, "display": compact(downloads), "icon": "📥"},
            {"label": "Reviews", "value": reviews, "display": compact(reviews), "icon": "⭐"},
            {"label": "API Calls", "value": api_calls, "display": compact(api_calls), "icon": "🔗"},
        ],
        "total_engagement": apps + developers + downloads + reviews,
    }
