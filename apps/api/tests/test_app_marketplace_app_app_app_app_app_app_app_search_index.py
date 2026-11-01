from app.services.app_marketplace_app_app_app_app_app_app_app_search_index import SearchIndexer

def test_index_search():
    si = SearchIndexer()
    si.index("d1", "Getting Started Guide", "Learn how to build extensions", ["docs"])
    si.index("d2", "API Reference", "REST API endpoints for users", ["api"])
    r = si.search("build extensions")
    assert len(r) >= 1
    assert r[0]["id"] == "d1"

def test_type_filter():
    si = SearchIndexer()
    si.index("d1", "Doc", "hello world", doc_type="docs")
    si.index("d2", "API", "hello api", doc_type="api")
    r = si.search("hello", doc_type="api")
    assert len(r) == 1
    assert r[0]["type"] == "api"
