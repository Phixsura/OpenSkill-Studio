"""App detail tabs — build tab content for each section of the app detail page."""


def build_overview_tab(*, app: dict, developer: dict, screenshots: list[str]) -> dict:
    return {"key": "overview", "title": "Overview",
            "content": {"description": app.get("description", ""),
                         "developer": developer.get("display_name"),
                         "category": app.get("category"),
                         "screenshots": screenshots[:6],
                         "features": app.get("features", [])}}


def build_reviews_tab(*, reviews: list[dict], stats: dict) -> dict:
    return {"key": "reviews", "title": f"Reviews ({stats.get('count', 0)})",
            "content": {"avg_rating": stats.get("avg_rating", 0),
                         "distribution": stats.get("distribution", {}),
                         "reviews": reviews[:20]}}


def build_changelog_tab(*, versions: list[dict]) -> dict:
    return {"key": "changelog", "title": f"Changelog ({len(versions)})",
            "content": {"versions": versions[:10],
                         "latest": versions[0] if versions else None}}


def build_support_tab(*, support_email: str | None, docs_url: str | None,
                         faq: list[dict]) -> dict:
    return {"key": "support", "title": "Support",
            "content": {"email": support_email, "docs_url": docs_url,
                         "faq": faq[:10], "has_email": support_email is not None}}


def build_all_tabs(*, app: dict, developer: dict, screenshots: list[str],
                      reviews: list[dict], review_stats: dict, versions: list[dict],
                      support_email: str | None, docs_url: str | None, faq: list[dict]) -> list[dict]:
    return [
        build_overview_tab(app=app, developer=developer, screenshots=screenshots),
        build_reviews_tab(reviews=reviews, stats=review_stats),
        build_changelog_tab(versions=versions),
        build_support_tab(support_email=support_email, docs_url=docs_url, faq=faq),
    ]
