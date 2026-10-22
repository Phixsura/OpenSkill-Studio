from app.services.app_marketplace_app_comparison_report import build_comparison_report

A = {"name": "App A", "slug": "a", "install_count": 200, "health_score": 95, "rating": 4.5, "rating_count": 50, "permissions": ["read:cohorts", "write:cohorts"], "sandbox": True}
B = {"name": "App B", "slug": "b", "install_count": 100, "health_score": 98, "rating": 4.0, "rating_count": 20, "permissions": ["read:cohorts", "subscribe:events"]}

def test_metrics():
    r = build_comparison_report(A, B)
    assert r["metrics"]["install_count"]["winner"] == "a"
    assert r["metrics"]["health_score"]["winner"] == "b"

def test_permissions():
    r = build_comparison_report(A, B)
    assert "write:cohorts" in r["permissions"]["only_a"]
    assert "subscribe:events" in r["permissions"]["only_b"]
    assert "read:cohorts" in r["permissions"]["shared"]

def test_features():
    r = build_comparison_report(A, B)
    assert r["features"]["a_has_sandbox"] is True
    assert r["features"]["b_has_sandbox"] is False

def test_recommendation():
    r = build_comparison_report(A, B)
    assert len(r["recommendation"]) > 0
