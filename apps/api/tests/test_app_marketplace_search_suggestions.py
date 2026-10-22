from app.services.app_marketplace_search_suggestions import build_suggestion_index, get_suggestions

def setup_function():
    build_suggestion_index([
        {"name": "LMS Connector", "category": "connector", "slug": "lms-conn"},
        {"name": "LMS Analytics", "category": "analytics", "slug": "lms-analytics"},
        {"name": "Auto Grader", "category": "automation", "slug": "auto-grader"},
    ])

def test_prefix_match():
    s = get_suggestions("lms")
    assert len(s) == 2

def test_single_match():
    s = get_suggestions("auto")
    assert "Auto Grader" in s

def test_empty_query():
    assert get_suggestions("") == []

def test_no_match():
    assert get_suggestions("xyz") == []

def test_limit():
    s = get_suggestions("l", limit=1)
    assert len(s) <= 1
