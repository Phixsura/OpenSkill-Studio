"""App Listing — manage marketplace listings for installed apps.

Manages app marketplace presence:
- Create and update listings with metadata
- Track install counts and ratings
- Listing status management (draft, published, unlisted)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

import structlog

log = structlog.get_logger()


class ListingStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    UNLISTED = "unlisted"


@dataclass
class AppListing:
    """A marketplace app listing."""

    listing_id: str
    name: str
    description: str
    category: str
    status: ListingStatus = ListingStatus.DRAFT
    icon_url: str = ""
    install_count: int = 0
    avg_rating: float = 0.0
    rating_count: int = 0
    tags: list[str] = field(default_factory=list)


class AppAppListing:
    """Manage marketplace listings."""

    def __init__(self) -> None:
        self._listings: dict[tuple[str, str], AppListing] = {}

    def create_listing(
        self,
        installation_id: str,
        listing_id: str,
        name: str,
        description: str,
        category: str,
        tags: list[str] | None = None,
        icon_url: str = "",
    ) -> AppListing:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not listing_id:
            raise ValueError("listing_id is required")
        if not name:
            raise ValueError("name is required")

        key = (installation_id, listing_id)
        if key in self._listings:
            raise ValueError(f"Listing {listing_id} already exists")

        listing = AppListing(
            listing_id=listing_id, name=name, description=description,
            category=category, tags=tags or [], icon_url=icon_url,
        )
        self._listings[key] = listing
        return listing

    def publish(self, installation_id: str, listing_id: str) -> AppListing:
        listing = self._get(installation_id, listing_id)
        if not listing.description:
            raise ValueError("Cannot publish without description")
        listing.status = ListingStatus.PUBLISHED
        return listing

    def unlist(self, installation_id: str, listing_id: str) -> AppListing:
        listing = self._get(installation_id, listing_id)
        listing.status = ListingStatus.UNLISTED
        return listing

    def record_install(self, installation_id: str, listing_id: str) -> AppListing:
        listing = self._get(installation_id, listing_id)
        listing.install_count += 1
        return listing

    def record_rating(
        self, installation_id: str, listing_id: str, rating: float
    ) -> AppListing:
        if not 1 <= rating <= 5:
            raise ValueError("Rating must be between 1 and 5")
        listing = self._get(installation_id, listing_id)
        total = listing.avg_rating * listing.rating_count + rating
        listing.rating_count += 1
        listing.avg_rating = round(total / listing.rating_count, 2)
        return listing

    def search(
        self, installation_id: str, query: str = "", category: str = ""
    ) -> list[AppListing]:
        listings = [
            l for (inst, _), l in self._listings.items()
            if inst == installation_id and l.status == ListingStatus.PUBLISHED
        ]
        if query:
            q = query.lower()
            listings = [l for l in listings if q in l.name.lower() or q in l.description.lower()]
        if category:
            listings = [l for l in listings if l.category == category]
        return sorted(listings, key=lambda l: l.install_count, reverse=True)

    def get_listing(self, installation_id: str, listing_id: str) -> AppListing:
        return self._get(installation_id, listing_id)

    def _get(self, installation_id: str, listing_id: str) -> AppListing:
        key = (installation_id, listing_id)
        l = self._listings.get(key)
        if l is None:
            raise KeyError(f"Listing {listing_id} not found")
        return l
