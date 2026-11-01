from app.services.app_marketplace_search_results_builder import build_search_results_page

def test_with_results():
    p = build_search_results_page(query="lms connector", results=[{"name": "X"}], total=1, page=1, per_page=20, filters={})
    assert p["has_results"] is True
    assert p["total_pages"] == 1

def test_no_results_suggestion():
    p = build_search_results_page(query="some complex query", results=[], total=0, page=1, per_page=20, filters={})
    assert p["has_results"] is False
    assert p["suggestion"] is not None

def test_single_word_no_suggestion():
    p = build_search_results_page(query="lms", results=[], total=0, page=1, per_page=20, filters={})
    assert p["suggestion"] is None
