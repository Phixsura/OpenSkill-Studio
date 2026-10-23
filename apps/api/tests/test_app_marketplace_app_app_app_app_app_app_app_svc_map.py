from app.services.app_marketplace_app_app_app_app_app_app_app_svc_map import build_service_map, find_isolated

def test_map():
    r = build_service_map([
        {"name": "api", "team": "platform", "language": "python", "calls": ["db", "cache"]},
        {"name": "web", "team": "frontend", "language": "typescript", "calls": ["api"]},
        {"name": "db", "team": "data", "language": "sql"},
        {"name": "cache", "team": "data", "language": "redis"},
        {"name": "cron", "team": "platform", "language": "python"},
    ])
    assert r["service_count"] == 5
    assert r["connection_count"] == 3
    assert "platform" in r["teams"]

def test_isolated():
    m = build_service_map([
        {"name": "api", "calls": ["db"]}, {"name": "db"}, {"name": "orphan"},
    ])
    iso = find_isolated(m)
    assert "orphan" in iso
