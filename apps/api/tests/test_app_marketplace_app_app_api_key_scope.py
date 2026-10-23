from app.services.app_marketplace_app_app_api_key_scope import build_scope_selector

def test_scopes():
    r = build_scope_selector(granted=["apps:read", "analytics:read"])
    assert r["granted"] == 2
    assert r["total_scopes"] == 8
    assert not r["has_high_risk"]
    assert "Apps" in r["categories"]

def test_high_risk():
    r = build_scope_selector(granted=["apps:delete"])
    assert r["has_high_risk"]
