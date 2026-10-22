"""Complete category page — compile all data for marketplace category page."""

from app.services.app_marketplace_category_page_builder import build_category_page

def build_complete_category_page(*, category: str, apps: list[dict], total: int,
                                    page: int, per_page: int, trending: list[dict]) -> dict:
    base = build_category_page(category=category, apps=apps, total=total, page=page, per_page=per_page)
    return {**base, "trending_in_category": trending[:5], "page_type": "category",
            "seo": {"title": f"{category.replace('_', ' ').title()} Apps | OpenSkill Marketplace"}}
