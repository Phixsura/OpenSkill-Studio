"""App API Developer Marketplace — manage app marketplace listings."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class MarketplaceListing:
    listing_id: str
    name: str
    description: str
    category: str
    install_count: int = 0
    rating: float = 0.0
    published: bool = False

class AppAPIDeveloperMarketplace:
    def __init__(self) -> None:
        self._listings: dict[tuple[str, str], MarketplaceListing] = {}

    def create(self, installation_id: str, listing_id: str, name: str, description: str, category: str) -> MarketplaceListing:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, listing_id)
        if key in self._listings: raise ValueError(f"Listing {listing_id} exists")
        l = MarketplaceListing(listing_id=listing_id, name=name, description=description, category=category)
        self._listings[key] = l
        return l

    def publish(self, installation_id: str, listing_id: str) -> MarketplaceListing:
        l = self._get(installation_id, listing_id)
        l.published = True
        return l

    def record_install(self, installation_id: str, listing_id: str) -> MarketplaceListing:
        l = self._get(installation_id, listing_id)
        l.install_count += 1
        return l

    def top_listings(self, installation_id: str, limit: int = 10) -> list[MarketplaceListing]:
        listings = [l for (inst, _), l in self._listings.items() if inst == installation_id and l.published]
        return sorted(listings, key=lambda l: l.install_count, reverse=True)[:limit]

    def by_category(self, installation_id: str, category: str) -> list[MarketplaceListing]:
        return [l for (inst, _), l in self._listings.items() if inst == installation_id and l.category == category and l.published]

    def list_all(self, installation_id: str) -> list[MarketplaceListing]:
        return [l for (inst, _), l in self._listings.items() if inst == installation_id]

    def _get(self, installation_id: str, listing_id: str) -> MarketplaceListing:
        l = self._listings.get((installation_id, listing_id))
        if l is None: raise KeyError(f"Listing {listing_id} not found")
        return l
