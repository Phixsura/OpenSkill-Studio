from app.services.app_marketplace_app_app_app_status_indicator import get_status_indicator, build_status_grid

def test_online():
    r = get_status_indicator(status="online", app_name="MyApp")
    assert r["icon"] == "🟢"
    assert r["is_healthy"]

def test_offline():
    r = get_status_indicator(status="offline")
    assert not r["is_healthy"]

def test_grid():
    apps = [{"name": "A", "status": "online"}, {"name": "B", "status": "degraded"}]
    r = build_status_grid(apps=apps)
    assert r["online"] == 1
    assert r["overall"] == "degraded"
