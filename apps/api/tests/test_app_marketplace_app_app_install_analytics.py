from app.services.app_marketplace_app_app_install_analytics import analyze_installs

def test_analyze():
    installs = [
        {"source": "search", "platform": "web", "date": "2026-10-23"},
        {"source": "search", "platform": "web", "date": "2026-10-23"},
        {"source": "referral", "platform": "mobile", "date": "2026-10-22"},
        {"source": "direct", "platform": "web", "date": "2026-10-22"},
    ]
    r = analyze_installs(installs=installs)
    assert r["total_installs"] == 4
    assert r["top_source"] == "search"
    assert r["by_platform"]["web"] == 3
    assert r["unique_days"] == 2

def test_empty():
    r = analyze_installs(installs=[])
    assert r["total_installs"] == 0
    assert r["top_source"] is None
