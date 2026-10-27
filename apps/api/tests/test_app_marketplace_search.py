"""Tests for App Marketplace Search — indexing, TF-IDF, facets, suggestions."""

import pytest

from app.services.app_marketplace_search import (
    AppListing,
    AppMarketplaceSearch,
    PriceTier,
    SortBy,
    _tokenize,
)


def _sample_listings() -> list[AppListing]:
    return [
        AppListing("app-1", "LMS Connector", "Sync grades and courses with your learning management system",
                    "connector", ["lms", "grades", "sync"], PriceTier.FREE, 4.5, 1200, "EduTech",
                    created_at="2026-10-01"),
        AppListing("app-2", "AI Rubric Generator", "Generate evaluation rubrics using AI models",
                    "evaluation", ["ai", "rubric", "grading"], PriceTier.PAID, 4.8, 800, "AITools",
                    created_at="2026-10-15"),
        AppListing("app-3", "Portfolio Exporter", "Export student portfolios to PDF and websites",
                    "export", ["portfolio", "pdf", "export"], PriceTier.FREEMIUM, 4.2, 2500, "ExportCo",
                    created_at="2026-09-20"),
        AppListing("app-4", "HRIS Sync", "Sync employee records with HR information systems",
                    "connector", ["hris", "hr", "sync"], PriceTier.PAID, 3.9, 300, "HRConnect",
                    created_at="2026-10-10"),
        AppListing("app-5", "Analytics Dashboard", "Real-time analytics and reporting dashboard",
                    "analytics", ["analytics", "dashboard", "reports"], PriceTier.FREE, 4.6, 3000, "DataViz",
                    created_at="2026-08-01"),
    ]


def _build_index() -> AppMarketplaceSearch:
    search = AppMarketplaceSearch()
    for listing in _sample_listings():
        search.index(listing)
    return search


class TestTokenize:
    def test_basic(self):
        tokens = _tokenize("Hello World")
        assert "hello" in tokens
        assert "world" in tokens

    def test_removes_stop_words(self):
        tokens = _tokenize("the quick and the lazy")
        assert "the" not in tokens
        assert "and" not in tokens
        assert "quick" in tokens

    def test_removes_short_words(self):
        tokens = _tokenize("a b cd ef")
        assert "a" not in tokens
        assert "b" not in tokens
        assert "cd" in tokens


class TestIndexing:
    def test_index_listings(self):
        search = _build_index()
        assert search.total_listings == 5

    def test_remove_listing(self):
        search = _build_index()
        search.remove("app-1")
        assert search.total_listings == 4
        result = search.search("LMS Connector")
        assert all(r.app.app_id != "app-1" for r in result.results)

    def test_update_listing(self):
        search = _build_index()
        updated = AppListing("app-1", "Super LMS Connector", "Updated description",
                             "connector", ["lms"], PriceTier.PAID, 4.9, 5000, "EduTech")
        search.index(updated)
        assert search.total_listings == 5
        result = search.search("Super LMS")
        assert len(result.results) > 0
        assert result.results[0].app.name == "Super LMS Connector"


class TestSearch:
    def test_search_by_name(self):
        search = _build_index()
        result = search.search("LMS Connector")
        assert len(result.results) > 0
        assert result.results[0].app.app_id == "app-1"

    def test_search_by_tag(self):
        search = _build_index()
        result = search.search("rubric")
        assert any(r.app.app_id == "app-2" for r in result.results)

    def test_search_by_description(self):
        search = _build_index()
        result = search.search("portfolio PDF export")
        assert any(r.app.app_id == "app-3" for r in result.results)

    def test_search_relevance_ordering(self):
        search = _build_index()
        result = search.search("sync", sort_by=SortBy.RELEVANCE)
        # app-1 and app-4 both have "sync"
        app_ids = [r.app.app_id for r in result.results]
        assert "app-1" in app_ids
        assert "app-4" in app_ids

    def test_search_highlights(self):
        search = _build_index()
        result = search.search("analytics dashboard")
        match = [r for r in result.results if r.app.app_id == "app-5"]
        assert len(match) == 1
        assert "analytics" in match[0].highlights
        assert "dashboard" in match[0].highlights

    def test_empty_query_returns_all(self):
        search = _build_index()
        result = search.search("")
        assert result.total == 5

    def test_no_results(self):
        search = _build_index()
        result = search.search("xyznonexistent")
        assert result.total == 0
        assert result.results == []


class TestFiltering:
    def test_filter_by_category(self):
        search = _build_index()
        result = search.search("", category="connector")
        assert result.total == 2
        assert all(r.app.category == "connector" for r in result.results)

    def test_filter_by_price_tier(self):
        search = _build_index()
        result = search.search("", price_tier=PriceTier.FREE)
        assert result.total == 2
        assert all(r.app.price_tier == PriceTier.FREE for r in result.results)

    def test_filter_by_min_rating(self):
        search = _build_index()
        result = search.search("", min_rating=4.5)
        assert all(r.app.rating >= 4.5 for r in result.results)

    def test_combined_filters(self):
        search = _build_index()
        result = search.search("sync", category="connector")
        assert result.total >= 1
        assert all(r.app.category == "connector" for r in result.results)


class TestSorting:
    def test_sort_by_downloads(self):
        search = _build_index()
        result = search.search("", sort_by=SortBy.DOWNLOADS)
        downloads = [r.app.downloads for r in result.results]
        assert downloads == sorted(downloads, reverse=True)

    def test_sort_by_rating(self):
        search = _build_index()
        result = search.search("", sort_by=SortBy.RATING)
        ratings = [r.app.rating for r in result.results]
        assert ratings == sorted(ratings, reverse=True)

    def test_sort_by_newest(self):
        search = _build_index()
        result = search.search("", sort_by=SortBy.NEWEST)
        dates = [r.app.created_at for r in result.results]
        assert dates == sorted(dates, reverse=True)


class TestPagination:
    def test_pagination(self):
        search = _build_index()
        p1 = search.search("", per_page=2, page=1)
        assert len(p1.results) == 2
        assert p1.has_more is True
        assert p1.total == 5

        p2 = search.search("", per_page=2, page=2)
        assert len(p2.results) == 2

        p3 = search.search("", per_page=2, page=3)
        assert len(p3.results) == 1
        assert p3.has_more is False


class TestFacets:
    def test_facets_returned(self):
        search = _build_index()
        result = search.search("")
        assert "category" in result.facets
        assert "price_tier" in result.facets
        assert result.facets["category"]["connector"] == 2
        assert result.facets["price_tier"]["free"] == 2


class TestSuggestions:
    def test_suggest(self):
        search = _build_index()
        suggestions = search.suggest("ana")
        assert "analytics" in suggestions

    def test_suggest_empty_prefix(self):
        search = _build_index()
        assert search.suggest("") == []

    def test_suggest_no_match(self):
        search = _build_index()
        assert search.suggest("zzz") == []

    def test_suggest_limit(self):
        search = _build_index()
        suggestions = search.suggest("s", limit=3)
        assert len(suggestions) <= 3
