"""App Store Provider — serve extension listings for the marketplace frontend.

Aggregates data from multiple services (registry, reviews, analytics)
into unified listing objects optimized for the storefront UI.
"""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class StoreListing:
    extension_id: str
    name: str
    icon: str
    author: str
    version: str
    short_description: str
    category: str
    tags: list[str]
    downloads: int
    rating: float
    review_count: int
    verified: bool = False
    featured: bool = False
    updated_at: str = ""


@dataclass
class StoreCollection:
    collection_id: str
    title: str
    description: str
    items: list[StoreListing] = field(default_factory=list)


class AppStoreProvider:
    """Provides curated store data for the marketplace frontend."""

    def __init__(self):
        self._listings: dict[str, StoreListing] = {}
        self._collections: dict[str, StoreCollection] = {}
        self._featured: list[str] = []

    def add_listing(self, listing: StoreListing) -> None:
        self._listings[listing.extension_id] = listing

    def get_listing(self, extension_id: str) -> StoreListing | None:
        return self._listings.get(extension_id)

    def search(self, query: str, category: str = "", limit: int = 20) -> list[StoreListing]:
        q = query.lower()
        results = [
            l for l in self._listings.values()
            if q in l.name.lower() or q in l.short_description.lower()
            or any(q in t.lower() for t in l.tags)
        ]
        if category:
            results = [l for l in results if l.category == category]
        results.sort(key=lambda l: l.downloads, reverse=True)
        return results[:limit]

    def get_featured(self, limit: int = 6) -> list[StoreListing]:
        return [self._listings[eid] for eid in self._featured
                if eid in self._listings][:limit]

    def set_featured(self, extension_ids: list[str]) -> None:
        self._featured = extension_ids

    def get_top_rated(self, limit: int = 10) -> list[StoreListing]:
        rated = [l for l in self._listings.values() if l.review_count >= 3]
        return sorted(rated, key=lambda l: l.rating, reverse=True)[:limit]

    def get_trending(self, limit: int = 10) -> list[StoreListing]:
        return sorted(self._listings.values(),
                      key=lambda l: l.downloads, reverse=True)[:limit]

    def get_by_category(self, category: str, limit: int = 20) -> list[StoreListing]:
        return sorted(
            [l for l in self._listings.values() if l.category == category],
            key=lambda l: l.downloads, reverse=True,
        )[:limit]

    def create_collection(self, collection_id: str, title: str, description: str,
                          extension_ids: list[str]) -> StoreCollection:
        items = [self._listings[eid] for eid in extension_ids if eid in self._listings]
        collection = StoreCollection(collection_id, title, description, items)
        self._collections[collection_id] = collection
        return collection

    def get_collection(self, collection_id: str) -> StoreCollection | None:
        return self._collections.get(collection_id)

    def get_store_home(self) -> dict:
        """Build the store homepage data."""
        return {
            "featured": self.get_featured(),
            "trending": self.get_trending(5),
            "top_rated": self.get_top_rated(5),
            "total_extensions": len(self._listings),
            "collections": list(self._collections.values()),
        }
