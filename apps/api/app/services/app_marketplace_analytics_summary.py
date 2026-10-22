"""Marketplace analytics summary — top-level marketplace performance metrics."""

def build_analytics_summary(*, total_page_views: int, unique_visitors: int, search_count: int,
                              install_count: int, conversion_rate: float) -> dict:
    return {
        "page_views": total_page_views,
        "unique_visitors": unique_visitors,
        "searches": search_count,
        "installs": install_count,
        "conversion_rate": round(conversion_rate, 2),
        "avg_views_per_install": round(total_page_views / install_count, 1) if install_count > 0 else 0,
    }
