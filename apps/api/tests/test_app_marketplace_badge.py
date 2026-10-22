from app.services.app_marketplace_badge import compute_badges

def test_popular():
    b = compute_badges(install_count=200, health_score=90, avg_latency_ms=150,
                       developer_verified=False, days_since_publish=60)
    assert any(badge["label"] == "Popular" for badge in b)

def test_all_badges():
    b = compute_badges(install_count=500, health_score=99, avg_latency_ms=50,
                       developer_verified=True, days_since_publish=5)
    assert len(b) == 5

def test_no_badges():
    b = compute_badges(install_count=0, health_score=50, avg_latency_ms=500,
                       developer_verified=False, days_since_publish=365)
    assert len(b) == 0

def test_new_only():
    b = compute_badges(install_count=0, health_score=50, avg_latency_ms=500,
                       developer_verified=False, days_since_publish=10)
    assert len(b) == 1 and b[0]["label"] == "New"
