"""Marketplace navigation builder — build navigation state."""

MARKETPLACE_PAGES = ["home", "apps", "categories", "featured", "trending", "developers"]

def build_nav_state(active_page: str) -> dict:
    return {"active": active_page, "pages": MARKETPLACE_PAGES, "is_valid": active_page in MARKETPLACE_PAGES}
