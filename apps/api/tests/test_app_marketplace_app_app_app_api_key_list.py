from app.services.app_marketplace_app_app_app_api_key_list import build_api_key_list, get_key_usage

def test_list():
    keys = [
        {"prefix": "osk_abc", "name": "Prod", "scopes": ["read"], "revoked": False, "requests_30d": 5000},
        {"prefix": "osk_def", "name": "Old", "scopes": [], "revoked": True, "requests_30d": 0},
    ]
    r = build_api_key_list(keys=keys)
    assert r["active"] == 1
    assert r["revoked"] == 1

def test_usage():
    counts = [{"date": "2026-01-01", "count": 100}, {"date": "2026-01-02", "count": 200}]
    r = get_key_usage(key_prefix="osk_abc", daily_counts=counts)
    assert r["total_requests"] == 300
    assert r["avg_daily"] == 150
    assert r["peak_daily"] == 200
