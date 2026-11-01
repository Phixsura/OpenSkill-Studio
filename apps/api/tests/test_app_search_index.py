"""Tests for App Search Index — indexing, search, facets."""

import pytest

from app.services.app_search_index import AppSearchIndex


class TestIndex:
    def test_index(self):
        s = AppSearchIndex()
        d = s.index_document("inst-1", "d1", "user", {"name": "Alice", "email": "alice@example.com"})
        assert d.doc_id == "d1"
        assert s.doc_count("inst-1") == 1

    def test_replace(self):
        s = AppSearchIndex()
        s.index_document("inst-1", "d1", "user", {"name": "Alice"})
        s.index_document("inst-1", "d1", "user", {"name": "Bob"})
        assert s.doc_count("inst-1") == 1

    def test_remove(self):
        s = AppSearchIndex()
        s.index_document("inst-1", "d1", "user", {"name": "Alice"})
        assert s.remove_document("inst-1", "d1") is True
        assert s.doc_count("inst-1") == 0


class TestSearch:
    def test_basic_search(self):
        s = AppSearchIndex()
        s.index_document("inst-1", "d1", "user", {"name": "Alice Smith", "bio": "Engineer"})
        s.index_document("inst-1", "d2", "user", {"name": "Bob Jones", "bio": "Designer"})
        hits = s.search("inst-1", "alice")
        assert len(hits) == 1
        assert hits[0].doc.doc_id == "d1"

    def test_multi_term(self):
        s = AppSearchIndex()
        s.index_document("inst-1", "d1", "user", {"name": "Alice", "bio": "Python engineer"})
        hits = s.search("inst-1", "alice python")
        assert hits[0].score >= 2.0

    def test_filter_by_type(self):
        s = AppSearchIndex()
        s.index_document("inst-1", "d1", "user", {"name": "Alice"})
        s.index_document("inst-1", "d2", "project", {"name": "Alice Project"})
        hits = s.search("inst-1", "alice", doc_type="user")
        assert len(hits) == 1

    def test_empty_query(self):
        s = AppSearchIndex()
        with pytest.raises(ValueError):
            s.search("inst-1", "")

    def test_no_results(self):
        s = AppSearchIndex()
        s.index_document("inst-1", "d1", "user", {"name": "Alice"})
        assert s.search("inst-1", "nonexistent") == []


class TestFacets:
    def test_facets(self):
        s = AppSearchIndex()
        s.index_document("inst-1", "d1", "user", {"name": "A", "role": "admin"})
        s.index_document("inst-1", "d2", "user", {"name": "B", "role": "admin"})
        s.index_document("inst-1", "d3", "user", {"name": "C", "role": "member"})
        facets = s.facets("inst-1", "role")
        assert facets["admin"] == 2
        assert facets["member"] == 1


class TestIsolation:
    def test_cross_installation(self):
        s = AppSearchIndex()
        s.index_document("inst-1", "d1", "user", {"name": "Alice"})
        assert s.search("inst-2", "alice") == []
