from app.services.app_marketplace_trending_calculator import compute_trending_with_decay, rank_trending_apps

def test_new_app_higher():
    new = compute_trending_with_decay(installs_7d=10, executions_7d=100, reviews_7d=2, health_score=95, days_since_publish=1)
    old = compute_trending_with_decay(installs_7d=10, executions_7d=100, reviews_7d=2, health_score=95, days_since_publish=90)
    assert new > old

def test_healthy_higher():
    healthy = compute_trending_with_decay(installs_7d=10, executions_7d=0, reviews_7d=0, health_score=100, days_since_publish=0)
    sick = compute_trending_with_decay(installs_7d=10, executions_7d=0, reviews_7d=0, health_score=50, days_since_publish=0)
    assert healthy > sick

def test_rank():
    apps = [{"name": "low", "installs_7d": 1}, {"name": "high", "installs_7d": 100, "health_score": 100}]
    ranked = rank_trending_apps(apps, limit=2)
    assert ranked[0]["name"] == "high"
