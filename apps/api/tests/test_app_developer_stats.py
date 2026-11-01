"""Developer stats tests."""
from app.services.app_developer_stats import compute_developer_stats

def test_basic():
    s = compute_developer_stats(app_count=10, published_count=6, total_installs=200)
    assert s["draft_count"] == 4
    assert s["publish_rate"] == 60.0

def test_empty():
    s = compute_developer_stats()
    assert s["app_count"] == 0
    assert s["publish_rate"] == 0

def test_all_published():
    s = compute_developer_stats(app_count=5, published_count=5)
    assert s["publish_rate"] == 100.0

def test_health_rounded():
    s = compute_developer_stats(avg_health_score=95.555)
    assert s["avg_health_score"] == 95.6
