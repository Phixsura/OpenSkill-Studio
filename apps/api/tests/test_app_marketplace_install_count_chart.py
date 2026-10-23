from app.services.app_marketplace_install_count_chart import aggregate_daily_installs, compute_install_growth, get_peak_install_day

def test_aggregate():
    installs = [{"installed_at": "2026-10-01T10:00:00Z"}, {"installed_at": "2026-10-01T14:00:00Z"},
                {"installed_at": "2026-10-02T10:00:00Z"}]
    r = aggregate_daily_installs(installs=installs)
    assert r[0]["date"] == "2026-10-01"
    assert r[0]["count"] == 2

def test_growth_up():
    daily = [{"date": f"d{i}", "count": 5} for i in range(5)] + [{"date": f"d{i+5}", "count": 15} for i in range(5)]
    r = compute_install_growth(daily_data=daily)
    assert r["trend"] == "up"

def test_growth_stable():
    daily = [{"date": f"d{i}", "count": 10} for i in range(10)]
    r = compute_install_growth(daily_data=daily)
    assert r["trend"] == "stable"

def test_peak():
    daily = [{"date": "d1", "count": 5}, {"date": "d2", "count": 20}, {"date": "d3", "count": 8}]
    p = get_peak_install_day(daily_data=daily)
    assert p["date"] == "d2"
    assert p["count"] == 20
