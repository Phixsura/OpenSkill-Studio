from app.services.app_marketplace_category_stats import compute_category_stats

def test_basic():
    apps = [
        {"category": "connector", "install_count": 100, "health_score": 95},
        {"category": "connector", "install_count": 50, "health_score": 85},
        {"category": "automation", "install_count": 200, "health_score": 100},
    ]
    stats = compute_category_stats(apps)
    assert stats[0]["category"] == "connector"
    assert stats[0]["count"] == 2
    assert stats[0]["installs"] == 150

def test_empty():
    assert compute_category_stats([]) == []

def test_avg_health():
    apps = [{"category": "x", "health_score": 80}, {"category": "x", "health_score": 100}]
    stats = compute_category_stats(apps)
    assert stats[0]["avg_health"] == 90.0

def test_sorted_by_count():
    apps = [{"category": "a"}, {"category": "b"}, {"category": "b"}]
    stats = compute_category_stats(apps)
    assert stats[0]["category"] == "b"
