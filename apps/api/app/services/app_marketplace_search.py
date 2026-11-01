"""App Marketplace Search — in-memory full-text search index for the app marketplace.

Provides search and discovery for the developer platform marketplace:
- Full-text search across name, description, tags, category
- TF-IDF-style relevance scoring
- Faceted filtering: category, price tier, rating range
- Sort: relevance, downloads, rating, newest
- Pagination with total count
- Auto-complete suggestions from indexed terms
"""

from __future__ import annotations

import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from enum import Enum

import structlog

log = structlog.get_logger()

STOP_WORDS = frozenset({
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "is", "it", "as", "be", "this", "that", "from",
})

WORD_RE = re.compile(r"[a-z0-9]+")


class PriceTier(str, Enum):
    FREE = "free"
    PAID = "paid"
    FREEMIUM = "freemium"


class SortBy(str, Enum):
    RELEVANCE = "relevance"
    DOWNLOADS = "downloads"
    RATING = "rating"
    NEWEST = "newest"


@dataclass
class AppListing:
    """A marketplace app listing."""

    app_id: str
    name: str
    description: str
    category: str
    tags: list[str]
    price_tier: PriceTier
    rating: float         # 0.0 - 5.0
    downloads: int
    publisher: str
    icon: str = "📦"
    created_at: str = ""  # ISO date


@dataclass
class SearchResult:
    """A single search hit."""

    app: AppListing
    score: float
    highlights: list[str]  # matching terms


@dataclass
class SearchResponse:
    """Paginated search response."""

    results: list[SearchResult]
    total: int
    page: int
    per_page: int
    has_more: bool
    facets: dict[str, dict[str, int]]  # field → value → count


def _tokenize(text: str) -> list[str]:
    """Tokenize and normalize text for indexing."""
    return [w for w in WORD_RE.findall(text.lower()) if w not in STOP_WORDS and len(w) > 1]


class AppMarketplaceSearch:
    """In-memory search index for marketplace apps."""

    def __init__(self):
        # app_id → AppListing
        self._listings: dict[str, AppListing] = {}
        # term → set of app_ids
        self._index: dict[str, set[str]] = defaultdict(set)
        # app_id → term → count (for TF)
        self._term_freq: dict[str, Counter] = {}
        # term → document frequency (how many listings contain this term)
        self._doc_freq: Counter = Counter()
        self._total_docs = 0

    def index(self, listing: AppListing) -> None:
        """Add or update a listing in the search index."""
        # Remove old entry if updating
        if listing.app_id in self._listings:
            self._remove_from_index(listing.app_id)

        self._listings[listing.app_id] = listing
        self._total_docs = len(self._listings)

        # Build searchable text
        text = " ".join([
            listing.name, listing.name,  # boost name
            listing.description,
            listing.category,
            " ".join(listing.tags),
            listing.publisher,
        ])
        tokens = _tokenize(text)
        tf = Counter(tokens)
        self._term_freq[listing.app_id] = tf

        for term in set(tokens):
            self._index[term].add(listing.app_id)
            self._doc_freq[term] += 1

    def remove(self, app_id: str) -> None:
        self._remove_from_index(app_id)
        self._listings.pop(app_id, None)
        self._total_docs = len(self._listings)

    def search(self, query: str, category: str | None = None,
               price_tier: PriceTier | None = None,
               min_rating: float | None = None,
               sort_by: SortBy = SortBy.RELEVANCE,
               page: int = 1, per_page: int = 20) -> SearchResponse:
        """Search the marketplace index."""
        query_tokens = _tokenize(query) if query.strip() else []

        # Score each listing
        scored: list[tuple[AppListing, float, list[str]]] = []

        if query_tokens:
            # Find candidate app_ids (union of term matches)
            candidates: set[str] = set()
            for term in query_tokens:
                candidates |= self._index.get(term, set())

            for app_id in candidates:
                listing = self._listings.get(app_id)
                if listing is None:
                    continue
                score, highlights = self._compute_score(app_id, query_tokens)
                if score > 0:
                    scored.append((listing, score, highlights))
        else:
            # No query → return all
            scored = [(listing, 0.0, []) for listing in self._listings.values()]

        # Filter
        if category:
            scored = [(a, s, h) for a, s, h in scored if a.category == category]
        if price_tier:
            scored = [(a, s, h) for a, s, h in scored if a.price_tier == price_tier]
        if min_rating is not None:
            scored = [(a, s, h) for a, s, h in scored if a.rating >= min_rating]

        total = len(scored)

        # Sort
        if sort_by == SortBy.RELEVANCE:
            scored.sort(key=lambda x: x[1], reverse=True)
        elif sort_by == SortBy.DOWNLOADS:
            scored.sort(key=lambda x: x[0].downloads, reverse=True)
        elif sort_by == SortBy.RATING:
            scored.sort(key=lambda x: x[0].rating, reverse=True)
        elif sort_by == SortBy.NEWEST:
            scored.sort(key=lambda x: x[0].created_at, reverse=True)

        # Facets (computed on filtered set)
        facets = self._compute_facets([a for a, _, _ in scored])

        # Paginate
        start = (page - 1) * per_page
        page_items = scored[start : start + per_page]

        return SearchResponse(
            results=[SearchResult(app=a, score=round(s, 4), highlights=h)
                     for a, s, h in page_items],
            total=total,
            page=page,
            per_page=per_page,
            has_more=start + per_page < total,
            facets=facets,
        )

    def suggest(self, prefix: str, limit: int = 10) -> list[str]:
        """Auto-complete suggestions from indexed terms."""
        prefix = prefix.lower().strip()
        if len(prefix) < 2:
            return []
        matches = sorted(
            [t for t in self._index if t.startswith(prefix)],
            key=lambda t: self._doc_freq[t],
            reverse=True,
        )
        return matches[:limit]

    @property
    def total_listings(self) -> int:
        return self._total_docs

    # ── Internals ────────────────────────────────────────

    def _compute_score(self, app_id: str, query_tokens: list[str]) -> tuple[float, list[str]]:
        """TF-IDF scoring."""
        tf = self._term_freq.get(app_id, Counter())
        score = 0.0
        highlights: list[str] = []

        for term in query_tokens:
            term_tf = tf.get(term, 0)
            if term_tf == 0:
                continue
            df = self._doc_freq.get(term, 0)
            idf = math.log(1 + self._total_docs / (1 + df))
            score += term_tf * idf
            highlights.append(term)

        return score, highlights

    def _remove_from_index(self, app_id: str) -> None:
        tf = self._term_freq.pop(app_id, None)
        if tf:
            for term in tf:
                if term in self._index:
                    self._index[term].discard(app_id)
                    if not self._index[term]:
                        del self._index[term]
                self._doc_freq[term] -= 1
                if self._doc_freq[term] <= 0:
                    del self._doc_freq[term]

    @staticmethod
    def _compute_facets(listings: list[AppListing]) -> dict[str, dict[str, int]]:
        categories: Counter = Counter()
        tiers: Counter = Counter()
        for a in listings:
            categories[a.category] += 1
            tiers[a.price_tier.value] += 1
        return {
            "category": dict(categories.most_common()),
            "price_tier": dict(tiers.most_common()),
        }
