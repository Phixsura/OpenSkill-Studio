from app.services.app_marketplace_trending import compute_trending_score, rank_trending

def test_score():
    s = compute_trending_score(recent_installs=10, recent_executions=100, recent_reviews=2)
    assert s == 10 * 3.0 + 100 * 0.1 + 2 * 5.0

def test_score_zero():
    assert compute_trending_score(recent_installs=0, recent_executions=0, recent_reviews=0) == 0

def test_rank():
    apps = [
        {"name": "low", "recent_installs": 1, "recent_executions": 0, "recent_reviews": 0},
        {"name": "high", "recent_installs": 50, "recent_executions": 1000, "recent_reviews": 10},
    ]
    ranked = rank_trending(apps)
    assert ranked[0]["name"] == "high"

def test_rank_limit():
    apps = [{"name": f"a{i}", "recent_installs": i} for i in range(20)]
    assert len(rank_trending(apps, limit=5)) == 5
