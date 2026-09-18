"""Tests for gaps #66-80: Search & Matching Intelligence."""

from app.talent.services.search_intelligence import (
    COMPENSATION_RANGES,
    EXPERIENCE_LEVELS,
    MATCH_FEEDBACK_OPTIONS,
    ORG_SIZE_RANGES,
    SearchAnalyticsStore,
    SearchCache,
    apply_boolean_filter,
    classify_match_tier,
    filter_by_tier,
    generate_search_suggestions,
    parse_boolean_query,
    validate_match_feedback,
)


class TestBooleanSearch:
    def test_simple_and(self):
        result = parse_boolean_query("Python AND Django")
        assert "python" in result["must"]
        assert "django" in result["must"]

    def test_or(self):
        result = parse_boolean_query("React OR Vue")
        assert "react" in result["must"] or "react" in result["should"]

    def test_not(self):
        result = parse_boolean_query("JavaScript NOT jQuery")
        assert "javascript" in result["must"]
        assert "jquery" in result["must_not"]

    def test_quoted_phrase(self):
        result = parse_boolean_query('"machine learning"')
        assert "machine learning" in result["must"]

    def test_apply_filter_must(self):
        items = [{"title": "Python Developer"}, {"title": "Java Developer"}]
        parsed = {"must": ["python"], "should": [], "must_not": []}
        filtered = apply_boolean_filter(items, parsed)
        assert len(filtered) == 1

    def test_apply_filter_must_not(self):
        items = [{"title": "Python Django"}, {"title": "Python Flask"}]
        parsed = {"must": ["python"], "should": [], "must_not": ["django"]}
        filtered = apply_boolean_filter(items, parsed)
        assert len(filtered) == 1
        assert "Flask" in filtered[0]["title"]


class TestSearchAnalytics:
    def test_record_and_stats(self):
        store = SearchAnalyticsStore()
        store.record("python", 10)
        store.record("react", 0)
        store.record("python", 5)
        stats = store.get_stats()
        assert stats["total_searches"] == 3
        assert stats["zero_result_count"] == 1

    def test_popular_queries(self):
        store = SearchAnalyticsStore()
        for _ in range(5):
            store.record("python", 10)
        store.record("react", 3)
        popular = store.get_popular_queries()
        assert popular[0]["query"] == "python"
        assert popular[0]["count"] == 5

    def test_zero_result_queries(self):
        store = SearchAnalyticsStore()
        store.record("nonexistent", 0)
        store.record("nonexistent", 0)
        zeros = store.get_zero_result_queries()
        assert zeros[0]["count"] == 2


class TestSearchCache:
    def test_set_and_get(self):
        cache = SearchCache(ttl_seconds=60)
        cache.set("key1", [{"id": "1"}])
        result = cache.get("key1")
        assert result == [{"id": "1"}]

    def test_miss(self):
        cache = SearchCache()
        assert cache.get("nonexistent") is None

    def test_clear(self):
        cache = SearchCache()
        cache.set("a", [])
        cache.set("b", [])
        cache.clear()
        assert cache.size == 0


class TestMatchTiers:
    def test_strong(self):
        assert classify_match_tier(0.90) == "strong"

    def test_good(self):
        assert classify_match_tier(0.65) == "good"

    def test_partial(self):
        assert classify_match_tier(0.45) == "partial"

    def test_weak(self):
        assert classify_match_tier(0.20) == "weak"

    def test_filter_by_tier(self):
        matches = [
            {"composite_score": 0.9},
            {"composite_score": 0.5},
            {"composite_score": 0.3},
        ]
        strong = filter_by_tier(matches, "strong")
        assert len(strong) == 1


class TestMatchFeedback:
    def test_valid(self):
        assert validate_match_feedback("helpful") == []

    def test_invalid(self):
        errors = validate_match_feedback("invalid")
        assert len(errors) > 0

    def test_all_options(self):
        assert len(MATCH_FEEDBACK_OPTIONS) == 5


class TestSearchSuggestions:
    def test_generates(self):
        suggestions = generate_search_suggestions(
            "py",
            ["python jobs", "react dev"],
            ["Python", "PyTorch"],
        )
        assert "Python" in suggestions or "PyTorch" in suggestions

    def test_short_query(self):
        assert generate_search_suggestions("p", [], []) == []


class TestFilterConstants:
    def test_compensation_ranges(self):
        assert len(COMPENSATION_RANGES) >= 5

    def test_experience_levels(self):
        assert "entry" in EXPERIENCE_LEVELS
        assert "senior" in EXPERIENCE_LEVELS

    def test_org_sizes(self):
        assert "startup" in ORG_SIZE_RANGES
        assert "enterprise" in ORG_SIZE_RANGES
