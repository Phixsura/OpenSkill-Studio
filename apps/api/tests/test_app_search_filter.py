from app.services.app_search_filter import build_search_filters, apply_filters

APPS = [
    {"name": "LMS Conn", "category": "connector", "health_score": 95, "install_count": 100, "developer_verified": True, "description": "LMS integration"},
    {"name": "Auto Grade", "category": "automation", "health_score": 80, "install_count": 20, "developer_verified": False, "description": "Auto grading"},
]

def test_build():
    f = build_search_filters(query="LMS", category="connector")
    assert f["query"] == "LMS"
    assert f["category"] == "connector"

def test_filter_query():
    results = apply_filters(APPS, {"query": "lms"})
    assert len(results) == 1

def test_filter_category():
    results = apply_filters(APPS, {"category": "automation"})
    assert len(results) == 1

def test_filter_health():
    results = apply_filters(APPS, {"min_health": 90})
    assert len(results) == 1

def test_filter_verified():
    results = apply_filters(APPS, {"verified_only": True})
    assert len(results) == 1
    assert results[0]["name"] == "LMS Conn"
