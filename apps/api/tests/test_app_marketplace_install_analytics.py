from app.services.app_marketplace_install_analytics import compute_install_velocity, compute_install_sources, compute_install_funnel

def test_velocity_accelerating():
    daily = [{"count": 10}] * 14 + [{"count": 30}] * 7
    r = compute_install_velocity(daily_installs=daily)
    assert r["trend"] == "accelerating"

def test_velocity_stable():
    daily = [{"count": 10}] * 14
    r = compute_install_velocity(daily_installs=daily)
    assert r["trend"] == "stable"

def test_sources():
    installs = [{"source": "search"}, {"source": "search"}, {"source": "direct"}, {"source": "referral"}]
    r = compute_install_sources(installs=installs)
    assert r[0]["source"] == "search"
    assert r[0]["pct"] == 50.0

def test_funnel():
    f = compute_install_funnel(page_views=10000, detail_views=3000, install_clicks=500, installs_completed=200)
    assert f["overall_rate"] == 2.0
    assert f["steps"][1]["rate"] == 30.0
