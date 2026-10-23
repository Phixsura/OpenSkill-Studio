from app.services.app_marketplace_app_app_app_app_app_app_app_search_index import (
    index_document, search, index_stats, clear_index,
)

def test_search():
    clear_index()
    index_document("d1", "Python FastAPI web framework")
    index_document("d2", "React TypeScript frontend web")
    index_document("d3", "Database PostgreSQL backend")
    r = search("web framework")
    assert r["total_matches"] >= 1
    assert r["results"][0]["id"] == "d1"  # both terms match
    assert r["results"][0]["score"] == 1.0
    clear_index()

def test_stats():
    clear_index()
    index_document("a", "hello world")
    index_document("b", "foo bar baz")
    s = index_stats()
    assert s["total_documents"] == 2
    assert s["total_words"] == 5
    clear_index()
