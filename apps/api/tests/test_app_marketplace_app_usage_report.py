from app.services.app_marketplace_app_usage_report import generate_usage_report, build_highlights, compare_periods

def test_report():
    r = generate_usage_report(app_id="a1", period="2026-10",
                               metrics={"api_calls": 50000, "unique_users": 200, "uptime_pct": 99.95, "error_count": 0, "new_installs": 15})
    assert r["summary"]["api_calls"] == 50000
    assert len(r["highlights"]) >= 3

def test_no_highlights():
    h = build_highlights({"api_calls": 100, "uptime_pct": 90, "error_count": 5})
    assert "No notable" in h[0]

def test_compare():
    c = compare_periods(current={"api_calls": 60000, "unique_users": 250, "error_count": 5},
                         previous={"api_calls": 50000, "unique_users": 200, "error_count": 10})
    assert c["api_calls"]["change_pct"] == 20.0
    assert c["error_count"]["change_pct"] == -50.0
