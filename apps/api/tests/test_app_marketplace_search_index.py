from app.services.app_marketplace_search_index import index_app, search, clear_index

def setup_function():
    clear_index()

def test_index_and_search():
    index_app({"id": "a1", "name": "LMS Connector", "description": "Connect to LMS", "category": "connector"})
    results = search("LMS")
    assert len(results) == 1
    assert results[0]["id"] == "a1"

def test_no_results():
    index_app({"id": "a1", "name": "Test App"})
    assert search("nonexistent") == []

def test_multiple_matches():
    index_app({"id": "a1", "name": "Analytics Dashboard"})
    index_app({"id": "a2", "name": "Analytics Reporter"})
    results = search("analytics")
    assert len(results) == 2

def test_ranking():
    index_app({"id": "a1", "name": "LMS Tool", "description": "basic"})
    index_app({"id": "a2", "name": "LMS Connector", "description": "LMS integration for LMS"})
    results = search("LMS")
    assert results[0]["id"] == "a2"  # More matches = higher rank

def test_empty_query():
    index_app({"id": "a1", "name": "X"})
    results = search("")
    assert len(results) >= 1
