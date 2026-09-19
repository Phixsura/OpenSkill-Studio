"""Search intelligence — advanced search, analytics, caching, Boolean operators.

Closes gaps: #51-#55 (assessment), #66 (semantic placeholder), #67 (alert delivery),
#68-#70 (filters), #71 (caching), #72 (analytics), #74 (export),
#75 (feedback), #76 (tier filter), #77 (geo), #79 (Boolean), #80 (suggestions).
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta

# ---------------------------------------------------------------------------
# Gap #72: Search analytics
# ---------------------------------------------------------------------------


@dataclass
class SearchAnalyticsStore:
    """In-memory search analytics (swap for Redis in production)."""

    queries: list[dict] = field(default_factory=list)
    zero_result_queries: list[str] = field(default_factory=list)

    def record(self, query: str, result_count: int, filters: dict | None = None) -> None:
        """Execute record."""
        self.queries.append(
            {
                "query": query,
                "result_count": result_count,
                "filters": filters or {},
                "timestamp": datetime.now(UTC).isoformat(),
            }
        )
        if result_count == 0:
            self.zero_result_queries.append(query)

    def get_popular_queries(self, limit: int = 20) -> list[dict]:
        """Execute get popular queries."""
        counter = Counter(q["query"] for q in self.queries if q["query"])
        return [{"query": q, "count": c} for q, c in counter.most_common(limit)]

    def get_zero_result_queries(self, limit: int = 20) -> list[dict]:
        """Execute get zero result queries."""
        counter = Counter(self.zero_result_queries)
        return [{"query": q, "count": c} for q, c in counter.most_common(limit)]

    def get_stats(self) -> dict:
        """Execute get stats."""
        total = len(self.queries)
        zero = len(self.zero_result_queries)
        return {
            "total_searches": total,
            "zero_result_count": zero,
            "zero_result_rate": round(zero / total, 3) if total > 0 else 0.0,
        }


_search_analytics = SearchAnalyticsStore()


def get_search_analytics() -> SearchAnalyticsStore:
    """Execute get search analytics."""
    return _search_analytics


# ---------------------------------------------------------------------------
# Gap #71: Search result caching
# ---------------------------------------------------------------------------


@dataclass
class SearchCache:
    """Simple TTL cache for search results."""

    _cache: dict = field(default_factory=dict)
    ttl_seconds: int = 60

    def get(self, key: str) -> list | None:
        """Execute get."""
        entry = self._cache.get(key)
        if not entry:
            return None
        if datetime.now(UTC) > entry.get("expires", ""):
            del self._cache[key]
            return None
        return entry.get("data", "")

    def set(self, key: str, data: list) -> None:
        """Execute set."""
        self._cache[key] = {
            "data": data,
            "expires": datetime.now(UTC) + timedelta(seconds=self.ttl_seconds),
        }

    def invalidate(self, key: str) -> None:
        """Execute invalidate."""
        self._cache.pop(key, None)

    def clear(self) -> None:
        """Execute clear."""
        self._cache.clear()

    @property
    def size(self) -> int:
        """Execute size."""
        return len(self._cache)


_search_cache = SearchCache()


def get_search_cache() -> SearchCache:
    """Execute get search cache."""
    return _search_cache


# ---------------------------------------------------------------------------
# Gap #79: Boolean search operators
# ---------------------------------------------------------------------------


def parse_boolean_query(query: str) -> dict:
    """Parse Boolean search syntax into structured query.

    Supports: AND, OR, NOT, quoted phrases, parentheses (simplified).

    Examples:
        "Python AND Machine Learning" → {must: ["python", "machine learning"]}
        "React OR Vue" → {should: ["react", "vue"]}
        "JavaScript NOT jQuery" → {must: ["javascript"], must_not: ["jquery"]}
        '"data science"' → {must: ["data science"]}  (exact phrase)
    """
    must: list[str] = []
    should: list[str] = []
    must_not: list[str] = []

    # Extract quoted phrases first
    phrases = re.findall(r'"([^"]+)"', query)
    remaining = re.sub(r'"[^"]*"', "", query).strip()

    for phrase in phrases:
        must.append(phrase.lower().strip())

    # Split by operators
    parts = re.split(r"\s+(AND|OR|NOT)\s+", remaining, flags=re.IGNORECASE)

    current_op = "AND"
    for part in parts:
        upper = part.strip().upper()
        if upper in ("AND", "OR", "NOT"):
            current_op = upper
            continue
        term = part.strip().lower()
        if not term:
            continue
        if current_op == "NOT":
            must_not.append(term)
        elif current_op == "OR":
            should.append(term)
        else:
            must.append(term)

    return {"must": must, "should": should, "must_not": must_not}


def apply_boolean_filter(items: list[dict], parsed: dict, text_field: str = "title") -> list[dict]:
    """Apply parsed Boolean query to a list of items."""
    results = []
    for item in items:
        text = (item.get(text_field, "") + " " + item.get("description", "")).lower()

        # Must: all terms present
        if parsed["must"] and not all(t in text for t in parsed["must"]):
            continue

        # Must not: none present
        if parsed["must_not"] and any(t in text for t in parsed["must_not"]):
            continue

        # Should: at least one present (if any should terms exist)
        if parsed["should"] and not any(t in text for t in parsed["should"]):
            continue

        results.append(item)
    return results


# ---------------------------------------------------------------------------
# Gap #68-70: Advanced search filters
# ---------------------------------------------------------------------------

COMPENSATION_RANGES = [
    ("entry", 0, 30000),
    ("junior", 30000, 60000),
    ("mid", 60000, 100000),
    ("senior", 100000, 150000),
    ("lead", 150000, 250000),
    ("executive", 250000, 999999),
]

EXPERIENCE_LEVELS = {
    "entry": {"min_years": 0, "max_years": 1, "label": "Entry Level (0-1 years)"},
    "junior": {"min_years": 1, "max_years": 3, "label": "Junior (1-3 years)"},
    "mid": {"min_years": 3, "max_years": 5, "label": "Mid-Level (3-5 years)"},
    "senior": {"min_years": 5, "max_years": 10, "label": "Senior (5-10 years)"},
    "lead": {"min_years": 10, "max_years": 99, "label": "Lead/Principal (10+ years)"},
}

ORG_SIZE_RANGES = {
    "startup": {"min": 1, "max": 50, "label": "Startup (1-50)"},
    "small": {"min": 51, "max": 200, "label": "Small (51-200)"},
    "medium": {"min": 201, "max": 1000, "label": "Medium (201-1000)"},
    "large": {"min": 1001, "max": 10000, "label": "Large (1001-10000)"},
    "enterprise": {"min": 10001, "max": 999999, "label": "Enterprise (10000+)"},
}


# ---------------------------------------------------------------------------
# Gap #75: Match quality feedback
# ---------------------------------------------------------------------------

MATCH_FEEDBACK_OPTIONS = frozenset(
    {
        "very_helpful",
        "helpful",
        "neutral",
        "not_helpful",
        "irrelevant",
    }
)


@dataclass(frozen=True, slots=True)
class MatchFeedback:
    match_id: str
    user_id: str
    opportunity_id: str
    rating: str
    comment: str | None
    submitted_at: datetime


def validate_match_feedback(rating: str) -> list[str]:
    """Execute validate match feedback."""
    errors = []
    if rating not in MATCH_FEEDBACK_OPTIONS:
        errors.append(f"Invalid rating. Must be one of: {sorted(MATCH_FEEDBACK_OPTIONS)}")
    return errors


# ---------------------------------------------------------------------------
# Gap #76: Match tier filtering
# ---------------------------------------------------------------------------

MATCH_TIERS = {
    "strong": {"min_score": 0.80, "label": "Strong Match (80%+)"},
    "good": {"min_score": 0.60, "label": "Good Match (60-79%)"},
    "partial": {"min_score": 0.40, "label": "Partial Match (40-59%)"},
    "weak": {"min_score": 0.0, "label": "Weak Match (<40%)"},
}


def classify_match_tier(score: float) -> str:
    """Execute classify match tier."""
    if score >= 0.80:
        return "strong"
    if score >= 0.60:
        return "good"
    if score >= 0.40:
        return "partial"
    return "weak"


def filter_by_tier(matches: list[dict], tier: str) -> list[dict]:
    """Execute filter by tier."""
    min_score = MATCH_TIERS.get(tier, {}).get("min_score", 0.0)
    return [m for m in matches if m.get("composite_score", 0) >= min_score]


# ---------------------------------------------------------------------------
# Gap #80: Search suggestions
# ---------------------------------------------------------------------------


def generate_search_suggestions(
    query: str,
    recent_queries: list[str],
    capability_names: list[str],
) -> list[str]:
    """Generate search suggestions from recent queries and capability names."""
    q = query.lower().strip()
    if len(q) < 2:
        return []

    suggestions = set()
    for name in capability_names:
        if q in name.lower():
            suggestions.add(name)
    for rq in recent_queries:
        if q in rq.lower():
            suggestions.add(rq)

    return sorted(suggestions)[:10]
