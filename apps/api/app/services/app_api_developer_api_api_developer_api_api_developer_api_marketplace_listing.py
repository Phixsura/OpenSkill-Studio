"""App API Developer Marketplace Listing — manage app listings in the marketplace."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class MarketplaceListing:
    listing_id: str
    app_name: str
    description: str
    category: str  # "productivity", "analytics", "security", "communication", "devtools"
    pricing: str  # "free", "freemium", "paid"
    status: str = "draft"  # "draft", "review", "published", "rejected"
    installs: int = 0
    rating: float = 0.0
    review_count: int = 0

class AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiMarketplaceListing:
    def __init__(self) -> None:
        self._listings: dict[tuple[str, str], MarketplaceListing] = {}

    def create(self, installation_id: str, listing_id: str, app_name: str, description: str, category: str, pricing: str) -> MarketplaceListing:
        if not installation_id: raise ValueError("installation_id is required")
        valid_cats = {"productivity", "analytics", "security", "communication", "devtools"}
        if category not in valid_cats: raise ValueError("invalid category")
        if pricing not in ("free", "freemium", "paid"): raise ValueError("invalid pricing")
        key = (installation_id, listing_id)
        if key in self._listings: raise ValueError(f"Listing {listing_id} exists")
        l = MarketplaceListing(listing_id=listing_id, app_name=app_name, description=description, category=category, pricing=pricing)
        self._listings[key] = l
        return l

    def publish(self, installation_id: str, listing_id: str) -> MarketplaceListing:
        l = self._get(installation_id, listing_id)
        if not l.description: raise ValueError("Description required")
        l.status = "published"
        return l

    def install(self, installation_id: str, listing_id: str) -> MarketplaceListing:
        l = self._get(installation_id, listing_id)
        if l.status != "published": raise ValueError("Can only install published listings")
        l.installs += 1
        return l

    def popular(self, installation_id: str, limit: int = 10) -> list[MarketplaceListing]:
        listings = [l for (inst, _), l in self._listings.items() if inst == installation_id and l.status == "published"]
        return sorted(listings, key=lambda l: l.installs, reverse=True)[:limit]

    def by_category(self, installation_id: str, category: str) -> list[MarketplaceListing]:
        return [l for (inst, _), l in self._listings.items() if inst == installation_id and l.category == category and l.status == "published"]

    def all_listings(self, installation_id: str) -> list[MarketplaceListing]:
        return [l for (inst, _), l in self._listings.items() if inst == installation_id]

    def _get(self, installation_id: str, listing_id: str) -> MarketplaceListing:
        key = (installation_id, listing_id)
        l = self._listings.get(key)
        if l is None: raise KeyError(f"Listing {listing_id} not found")
        return l
